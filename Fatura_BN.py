## Invoice UBL (xml) data extraction 

#Fatura xml dosyasından veri alma. 09.04.2023 tarihinden Yunus Karagün tarafından yazılmıştır. Tüm hakları saklıdır. yunus.karagun@gmail.com


import numpy as np
import pandas as pd
import os
from lxml import etree
import xml.etree.ElementTree as ET

# ADL ubl veri alma

directory = 'D:/TR/XML_ADL'

df_list = []

for filename in os.listdir(directory):
    if filename.startswith('1790172159') and filename.endswith('.xml'):
        file_path = os.path.join(directory, filename)
        tree = ET.parse(file_path)
        root = tree.getroot()


        # specify the namespace prefixes and URLs
        ns = {
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        }

        # extract the invoice information
        invoice_number_elem = root.find(".//cbc:ID", ns)
        invoice_date_elem = root.find(".//cbc:IssueDate", ns)
        supplier_id_elem = root.find(".//cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID", ns)
        supplier_name_elem = root.find(".//cac:AccountingSupplierParty/cac:Party/cac:PartyName/cbc:Name", ns)
        buyer_name_elem = root.find('cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID="BAYINO"]', ns)
        
        
        invoice_number = invoice_number_elem.text if invoice_number_elem is not None else None
        invoice_date = invoice_date_elem.text if invoice_date_elem is not None else None
        supplier_id = supplier_id_elem.text if supplier_id_elem is not None else None
        supplier_name = supplier_name_elem.text if supplier_name_elem is not None else None
        buyer_name = buyer_name_elem.text if buyer_name_elem is not None else None


        # extract the line item information
        line_items = []
        for item in root.findall(".//cac:InvoiceLine", ns):
            line_number_elem = item.find(".//cbc:ID", ns)
            Item_Identification_elem=  item.find(".//cac:Item/cac:SellersItemIdentification/cbc:ID", ns)
            Item_name_elem= item.find(".//cac:Item/cbc:Description", ns)
            quantity_elem = item.find(".//cbc:InvoicedQuantity", ns)
            price_amount_elem=item.find("cac:Price/cbc:PriceAmount", ns)
            amount_elem = item.find(".//cbc:LineExtensionAmount", ns)
            taxamount_elem= item.find(".//cbc:TaxAmount", ns)
            taxpercent_elem= item.find(".//cbc:Percent", ns)
            discamount_elem= item.find(".//cbc:Amount", ns)
            discpercent_elem= item.find(".//cbc:MultiplierFactorNumeric", ns)

            line_number = line_number_elem.text if line_number_elem is not None else None
            Item_Identification= Item_Identification_elem.text  if Item_Identification_elem is not None else None
            Item_name= Item_name_elem.text  if Item_name_elem is not None else None
            quantity = quantity_elem.text if quantity_elem is not None else None
            price_amount=price_amount_elem.text if price_amount_elem is not None else None
            amount = amount_elem.text  if amount_elem is not None else None
            taxamount = taxamount_elem.text  if taxamount_elem is not None else None
            taxpercent = taxpercent_elem.text  if taxamount_elem is not None else None
            discamount = discamount_elem.text  if discamount_elem is not None else None
            discpercent = discpercent_elem.text  if discpercent_elem is not None else None
            
            

            line_items.append({
                "line_number": line_number,
                "Item_Identification": Item_Identification,
                "Item_name": Item_name,                
                "quantity": quantity,
                "price": price_amount,
                "amount": amount,
                "taxamount": taxamount,
                "taxpercent": taxpercent,
                "discamount": discamount,
                "discpercent": discpercent,
            })

        # create a dataframe from the extracted information
        df = pd.DataFrame({
            "invoice_date": [invoice_date],
            "invoice_number": [invoice_number],
            "supplier_id": [supplier_id],
            "supplier_name":[supplier_name],
            "buyer_name": [buyer_name],
            "line_items": [line_items]
        })
        df_line_items = pd.json_normalize(line_items)
        df = pd.concat([df, df_line_items], axis=1)
        df.drop('line_items', axis=1, inplace=True)
        df.fillna(method='ffill', inplace=True)

        df_list.append(df)

# concatenate all the DataFrames into a single DataFrame
df_final = pd.concat(df_list, axis=0, ignore_index=True)

#Veri türlerinin uygun olana geçirilmesi

# df_final["buyer_name"]=df_final["buyer_name"].replace("Sevk Yeri:","", regex=True)
df_final = df_final.astype({'invoice_date': 'datetime64',
                            'line_number': 'int64',
                            'quantity': 'float64',
                            'price': 'float64',
                            'amount': 'float64',
                            'taxamount': 'float64',
                            'taxpercent': 'float64',
                            'discamount': 'float64',
                            'discpercent': 'float64'})

data = {'Copyright Notice':  ['Tüm Hakları saklıdır.', 'Yunus Karagün tarafından 03.04.2023 tarihinde geliştirilmiştir.', 'İletişim için: yunus.karagun@gmail.com']
        }
Copyright = pd.DataFrame(data)

with pd.ExcelWriter("D:\TR\BN_Invoice_Data.xlsx") as writer: 
        Copyright.to_excel(writer, sheet_name='Copyright', index=False)
        df_final.to_excel(writer, sheet_name='Data')