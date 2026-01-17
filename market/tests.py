from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Product, ProductImage

# Create your tests here.
class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Valid 1x1 pixel GIF
        self.valid_image = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        
        self.product_data = {
            'name': 'Test Product',
            'brand': 'Test Brand',
            'category': 'Test Category',
            'price': '10.00',
            'description': 'Test Description',
            'image': SimpleUploadedFile(name='test_image.gif', content=self.valid_image, content_type='image/gif'),
            'stock': 10
        }

    def test_create_product_status_automation(self):
        # Case 1: Positive Stock -> Available
        data = self.product_data.copy()
        data['stock'] = 10
        # Need to provide uploaded_images as empty list or something if expected? No, it's optional.
        # But wait, self.product_data['image'] is a SimpleUploadedFile.
        # When copying dictionary, it might be reused or closed?
        # New SimpleUploadedFile for each request is safer.
        data['image'] = SimpleUploadedFile(name='test_image.gif', content=self.valid_image, content_type='image/gif')
        
        response = self.client.post('/api/market/products/', data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Create Failed: {response.data}")
            
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'available')
        
        # Case 2: Zero Stock -> Out of Stock
        data['name'] = 'Out of Stock Product'
        data['stock'] = 0
        data['image'] = SimpleUploadedFile(name='test_image_2.gif', content=self.valid_image, content_type='image/gif')
        
        response = self.client.post('/api/market/products/', data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Create Zero Stock Failed: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'out_of_stock')

    def test_update_product_status_automation(self):
        # Create product with positive stock
        product = Product.objects.create(
            name='Update Test',
            brand='Brand',
            category='Category',
            price=10.00,
            description='Desc',
            stock=5,
            image=SimpleUploadedFile(name='existing.gif', content=self.valid_image, content_type='image/gif')
        )
        self.assertEqual(product.status, 'available')
        
        # Update stock to 0 via API (PATCH)
        product_url = f'/api/market/products/{product.id}/'
        response = self.client.patch(product_url, {
            'stock': 0
        }, format='multipart')
        
        if response.status_code != status.HTTP_200_OK:
            print(f"Update Failed: {response.data}")
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'out_of_stock')
        
        # Update stock back to positive
        response = self.client.patch(product_url, {
            'stock': 5
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'available')
