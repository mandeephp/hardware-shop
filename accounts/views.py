from django.http import HttpResponse
from .models import Purchase, Bill
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_pdf(request, purchase_id):
    purchase = Purchase.objects.get(id=purchase_id)
    buyer_name = purchase.buyer_name
    bill_detail = Bill.objects.filter(purchase__buyer_name=buyer_name)
    template_path = 'admin/purchase_details.html'
    context = {
        'buyer': purchase,
        'bill_details': bill_detail
        }
    # Create a Django template object, load the template file and render it with context
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="purchase_details.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
