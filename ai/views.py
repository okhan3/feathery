from django.shortcuts import render

from ai.models import StatementInfo, Holding
from ai.utils.utils import convert_pdf_to_base64_images, openai_api_call, parse_response

def index(request):
    statement_infos = StatementInfo.objects.all()

    # Get the holdings for each statement from the database
    statement_holdings = {}
    for statement_info in statement_infos:
        statement_info.portfolio_value = f'${statement_info.portfolio_value:,.2f}'
        holdings = Holding.objects.filter(owner=statement_info)
        statement_holdings[statement_info.id] = holdings

    context = {
        'statement_infos': statement_infos,
        'statement_holdings': statement_holdings,
    }
    
    return render(request, 'index.html', context)

def extracted_info(request):
    context = {}
    if request.method == 'POST' and request.FILES['pdf_file']:
        file = request.FILES['pdf_file']
        file_name = file.name
        file_content = file.read()
        
        # Call util functions to extract info from the PDF
        base64_images = convert_pdf_to_base64_images(file_content)
        response = openai_api_call(base64_images)
        account_holder_name, portfolio_value, holdings_dict = parse_response(response.json())
        
        # Save to database
        stripped_portfolio_value = portfolio_value.replace('$', '').replace(',', '')
        statement_info = StatementInfo(owner=account_holder_name, portfolio_value=stripped_portfolio_value)
        statement_info.save()
        
        for name, price in holdings_dict.items():
            holding = Holding(owner=statement_info, name=name, price=price)
            holding.save()
        
        context = {
            'file_name': file_name,
            'account_holder_name': account_holder_name,
            'portfolio_value': portfolio_value,
            'holdings': holdings_dict,
        }
        
    return render(request, 'extracted_info.html', context)