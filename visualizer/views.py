from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.files.storage import default_storage
import uuid
import os
import logging

from .models import (
    OllamaConfiguration,
    UploadedFile,
    Conversation,
    Message,
    Visualization,
    ProcessingJob
)
from .serializers import (
    OllamaConfigurationSerializer,
    UploadedFileSerializer,
    ConversationSerializer,
    MessageSerializer,
    VisualizationSerializer,
    ProcessingJobSerializer,
    ChatRequestSerializer,
    FileUploadResponseSerializer
)
from .services import OllamaService, VisualizationGenerator
from .parsers import FileParser, DataSummarizer
from .validators import VisualizationValidator, apply_visualization_rules

logger = logging.getLogger(__name__)


class OllamaConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for Ollama model configurations"""
    queryset = OllamaConfiguration.objects.all()
    serializer_class = OllamaConfigurationSerializer

    @action(detail=False, methods=['post'])
    def auto_detect(self, request):
        """Auto-detect and configure available Ollama models"""
        ollama_service = OllamaService()
        
        if not ollama_service.check_connection():
            return Response(
                {'error': 'Ollama server not available. Please ensure Ollama is running.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        models = ollama_service.auto_detect_and_configure()
        serializer = self.get_serializer(models, many=True)
        
        return Response({
            'message': f'Detected {len(models)} model(s)',
            'models': serializer.data
        })

    @action(detail=True, methods=['post'])
    def set_active(self, request, pk=None):
        """Set a model as active"""
        config = self.get_object()
        ollama_service = OllamaService()
        result = ollama_service.set_active_model(config.model_name)
        
        if result:
            serializer = self.get_serializer(result)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Failed to set active model'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active model"""
        ollama_service = OllamaService()
        active_model = ollama_service.get_active_model()
        
        if active_model:
            serializer = self.get_serializer(active_model)
            return Response(serializer.data)
        
        return Response(
            {'error': 'No active model found'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=['post'])
    def pull_model(self, request):
        """Pull a new model from Ollama registry"""
        model_name = request.data.get('model_name')
        if not model_name:
            return Response(
                {'error': 'model_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ollama_service = OllamaService()
        success = ollama_service.pull_model(model_name)
        
        if success:
            # Auto-detect to add the new model
            ollama_service.auto_detect_and_configure()
            return Response({'message': f'Model {model_name} pulled successfully'})
        
        return Response(
            {'error': f'Failed to pull model {model_name}'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FileUploadViewSet(viewsets.ModelViewSet):
    """ViewSet for file uploads"""
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        """Upload and parse files"""
        files = request.FILES.getlist('files')
        session_id = request.data.get('session_id', str(uuid.uuid4()))
        
        if not files:
            return Response(
                {'error': 'No files provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_files = []
        
        for file in files:
            # Determine file type
            file_extension = file.name.split('.')[-1].lower()
            file_type_map = {
                'csv': 'csv',
                'json': 'json',
                'yaml': 'yaml',
                'yml': 'yaml',
                'xlsx': 'xlsx',
                'xls': 'xlsx',
                'pdf': 'pdf'
            }
            file_type = file_type_map.get(file_extension)
            
            if not file_type:
                continue

            # Save file
            uploaded_file = UploadedFile.objects.create(
                file=file,
                file_name=file.name,
                file_type=file_type,
                file_size=file.size,
                session_id=session_id
            )

            # Parse file
            try:
                file_path = uploaded_file.file.path
                parsed_data = FileParser.parse_file(file_path, file_type)
                
                # Summarize data for storage
                summarized_data = DataSummarizer.summarize_data(parsed_data)
                uploaded_file.parsed_data = summarized_data
                uploaded_file.save()
                
                uploaded_files.append({
                    'file_id': uploaded_file.id,
                    'file_name': uploaded_file.file_name,
                    'file_type': uploaded_file.file_type,
                    'file_size': uploaded_file.file_size,
                    'parsed': True
                })
            except Exception as e:
                logger.error(f"Error parsing file {file.name}: {str(e)}")
                uploaded_files.append({
                    'file_id': uploaded_file.id,
                    'file_name': uploaded_file.file_name,
                    'file_type': uploaded_file.file_type,
                    'file_size': uploaded_file.file_size,
                    'parsed': False,
                    'error': str(e)
                })

        return Response({
            'session_id': session_id,
            'files': uploaded_files,
            'message': f'Uploaded {len(uploaded_files)} file(s)'
        })

    @action(detail=False, methods=['get'])
    def by_session(self, request):
        """Get files by session ID"""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        files = self.queryset.filter(session_id=session_id)
        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for conversations"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    @action(detail=False, methods=['post'])
    def chat(self, request):
        """Process a chat message and generate visualizations"""
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message_text = serializer.validated_data['message']
        session_id = serializer.validated_data['session_id']
        file_ids = serializer.validated_data.get('file_ids', [])

        # Get or create conversation
        conversation, _ = Conversation.objects.get_or_create(
            session_id=session_id,
            defaults={'ollama_model': OllamaService().get_active_model()}
        )

        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            message_type='user',
            content=message_text
        )

        # Get file data
        files = UploadedFile.objects.filter(id__in=file_ids) if file_ids else UploadedFile.objects.filter(session_id=session_id)
        
        file_data = {}
        for file in files:
            if file.parsed_data:
                file_data[file.file_name] = file.parsed_data

        # Create processing job
        job_id = str(uuid.uuid4())
        job = ProcessingJob.objects.create(
            job_id=job_id,
            conversation=conversation,
            status='processing',
            started_at=timezone.now()
        )

        try:
            # Generate visualizations
            viz_generator = VisualizationGenerator()
            result = viz_generator.generate_visualizations(
                data=file_data,
                user_request=message_text,
                model_name=conversation.ollama_model.model_name if conversation.ollama_model else None
            )

            if not result:
                raise Exception("Failed to generate visualizations")

            # Validate and fix configuration
            validator = VisualizationValidator()
            is_valid, error_msg = validator.validate_config(result)
            
            if not is_valid:
                # Try to fix common issues
                result = validator.fix_common_issues(result)
                is_valid, error_msg = validator.validate_config(result)
                
                if not is_valid:
                    raise Exception(f"Invalid visualization config: {error_msg}")
            
            # Apply visualization rules and theming
            result = apply_visualization_rules(result)

            # Save AI message
            ai_message = Message.objects.create(
                conversation=conversation,
                message_type='ai',
                content=result.get('explanation', 'Generated visualizations'),
                metadata={'charts_count': len(result.get('charts', []))}
            )

            # Save visualizations
            charts_data = []
            for chart in result.get('charts', []):
                if viz_generator.validate_chart_config(chart):
                    viz = Visualization.objects.create(
                        conversation=conversation,
                        message=ai_message,
                        title=chart.get('title', 'Untitled Chart'),
                        chart_type=chart.get('type', 'bar'),
                        chart_config=chart,
                        explanation=result.get('explanation', '')
                    )
                    charts_data.append(VisualizationSerializer(viz).data)

            # Update job
            job.status = 'completed'
            job.progress = 100
            job.completed_at = timezone.now()
            job.result = {
                'explanation': result.get('explanation'),
                'charts': charts_data
            }
            job.save()

            return Response({
                'job_id': job_id,
                'message': MessageSerializer(ai_message).data,
                'visualizations': charts_data,
                'explanation': result.get('explanation', '')
            })

        except Exception as e:
            logger.error(f"Chat processing error: {str(e)}")
            
            # Update job with error
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()

            # Save error message
            error_message = Message.objects.create(
                conversation=conversation,
                message_type='ai',
                content=f"Sorry, I encountered an error: {str(e)}"
            )

            return Response({
                'job_id': job_id,
                'message': MessageSerializer(error_message).data,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def by_session(self, request):
        """Get conversation by session ID"""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            conversation = self.queryset.get(session_id=session_id)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ProcessingJobViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for processing jobs"""
    queryset = ProcessingJob.objects.all()
    serializer_class = ProcessingJobSerializer

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get job status by job_id"""
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            job = self.queryset.get(job_id=job_id)
            serializer = self.get_serializer(job)
            return Response(serializer.data)
        except ProcessingJob.DoesNotExist:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    ollama_service = OllamaService()
    ollama_status = ollama_service.check_connection()
    
    return Response({
        'status': 'healthy',
        'ollama_connected': ollama_status,
        'active_model': OllamaService().get_active_model().model_name if ollama_status else None
    })
