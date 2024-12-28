from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
import numpy as np
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from roboflow import Roboflow
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import logging
import base64

# Configure logging
logger = logging.getLogger(__name__)

# Roboflow configuration
rf = Roboflow(api_key="0r4klCQmalPo9Xw2xkj6")
project = rf.workspace().project("recyclableitems")
model = project.version(2).model

@method_decorator(csrf_exempt, name='dispatch')
class WasteDetectionView(LoginRequiredMixin, View):
    template_name = 'capture.html'
    
    def get(self, request):
        """Render the waste detection page."""
        return render(request, self.template_name)