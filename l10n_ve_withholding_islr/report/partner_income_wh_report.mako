<!DOCTYPE html SYSTEM
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<html>
    <head>
        <style type="text/css">
            ${css}
        </style>
    </head>

    <body style="border:0; margin: 0;" onload="subst()" >
      %for obj in objects :
        <table width="100%">
          <tr>
            <td width="25%">
                <div>${helper.embed_image('jpeg',str(obj.company_id.logo),100, 46)}</div>
                <div class="logoAndCompanyName">${obj.company_id.name or ''|entity}</div>
                <div class="logoAndCompanyName">RIF: ${obj.company_id.partner_id.vat[2:]|entity}</div>
            </td>
            <td width="75%">
              <table style="width: 100%; text-align:center;">
                <tr><td><div class="headerTitle"> COMPROBANTE DE RETENCIONES VARIAS DEL IMPUESTO SOBRE LA RENTA</div></td></tr>
                <tr><td><div class="headerSubTitle"> (DIFERENTES A SUELDOS Y SALARIOS Y DEMÁS REMUNERACIONES SIMILARES A PERSONAS NATURALES RESIDENTES) </div></td></tr>
              </table>
            </td>
          </tr>
        </table>
        <table width="100%">
          <tr>
            <td class="headerBodyCenter" width="50%">
                <div> AGENTE DE RETENCIÓN </div>
            </td>
            <td class="headerBodyCenter" width="50%">
                <div> BENEFICIARIO </div>
            </td>
          </tr>
          <tr>
            <td class="cellBodyCenter" width="50%">
                <div> ${obj.company_id.name or ''|entity} </div>
                <div> RIF: ${obj.company_id.partner_id.vat[2:]|entity} </div>
            </td>
            <td class="cellBodyCenter" width="50%">
                <div> ${obj.partner_id.name or ''|entity} </div>
                <div> ${obj.partner_id.vat and obj.partner_id.vat[2:] or 'FALTA RIF'|entity} </div>
            </td>
          </tr>
        </table>
        %if obj.iwdl_ids:
          <table width="100%">
            <tr>
              <td class="headerBodyCenter" width="20%"> <div> FACTURA </div> </td>
              <td class="headerBodyCenter" width="17.5%"> <div> NÚM. CONTROL </div> </td>
              <td class="headerBodyCenter" width="12.5%"> <div> FEC. FACT. </div> </td>
              <td class="headerBodyCenter" width="12.5%"> <div> BASE DE RET. </div> </td>
              <td class="headerBodyCenter" width="12.5%"> <div> PORC. RET. </div> </td>
              <td class="headerBodyCenter" width="12.5%"> <div> SUSTRAENDO </div> </td>
              <td class="headerBodyCenter" width="12.5%"> <div> RETENCIÓN </div> </td>
            </tr>
          </table>
        %endif
        %for iwdl_brw in obj.iwdl_ids:
        <!--<table class="basic_table" width="100%">-->
          <table width="100%">
            <tr>
              <td class="cellCenter" width="20.%"> <div> ${iwdl_brw.invoice_id.supplier_invoice_number} </div> </td>
              <td class="cellCenter" width="17.5%"> <div> ${iwdl_brw.invoice_id.nro_ctrl} </div> </td>
              <td class="cellCenter" width="12.5%"> <div> ${iwdl_brw.invoice_id.date_document} </div> </td>
              <td class="cellCenter" width="12.5%"> <div> ${iwdl_brw.base_amount} </div> </td>
              <td class="cellCenter" width="12.5%"> <div> ${iwdl_brw.retencion_islr} </div> </td>
              <td class="cellCenter" width="12.5%"> <div> ${iwdl_brw.subtract} </div> </td>
              <td class="cellCenter" width="12.5%"> <div> ${iwdl_brw.amount} </div> </td>
            </tr>
          </table>
        %endfor
      %endfor
    </body>
</html>
