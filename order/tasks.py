# orders/tasks.py
import logging
from io import BytesIO
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from weasyprint import HTML
from .models import Order

logger = logging.getLogger(__name__)

def generate_invoice_pdf(order_id, base_url):
    """
    Async task to generate and save PDF invoice
    """
    try:
        order = Order.objects.get(id=order_id)
        logger.info("Generating invoice PDF for order %s", order.id)
        
        context = {'order': order}
        html_string = render_to_string('order/pdf_invoice.html', context)
        
        html = HTML(
            string=html_string,
            base_url=base_url
        )
        
        with BytesIO() as buffer:
            html.write_pdf(target=buffer)
            buffer.seek(0)
            filename = f'invoices/order_{order.id}.pdf'
            order.invoice_pdf.save(
                filename, 
                ContentFile(buffer.read()),
                save=True
            )
        
        logger.info("Successfully generated invoice for order %s", order.id)
        return True
        
    except Exception as e:
        logger.exception("Invoice generation failed for order %s", order_id)
        return False

def invoice_generation_hook(task):
    """
    Callback for async invoice generation task
    """
    order_id = task.args[0]
    if task.success:
        if task.result:
            logger.info("Invoice task completed for order %s", order_id)
        else:
            logger.error("Invoice generation failed in task for order %s", order_id)
            # Add additional error handling here:
            # - Send notification to admin
            # - Retry the task
    else:
        logger.error("Invoice task failed for order %s: %s", order_id, task.result)