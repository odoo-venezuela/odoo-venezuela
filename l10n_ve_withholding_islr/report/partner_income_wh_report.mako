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
        <table>
          <tr>
            <td width="30%">
                <div>${helper.embed_image('jpeg',str(obj.company_id.logo),65, 30)}</div>
                <div class="celdaTotalTitulo">RIF: ${obj.company_id.partner_id.vat[2:]|entity}</div>
                <div class="celdaTotalTitulo">${obj.company_id.name or ''|entity}</div>
            </td>
            <td width="70%">
              <table style="width: 100%; text-align:center;">
                <tr><td><div class="td_company_title"> COMPROBANTE DE RETENCIONES VARIAS DEL IMPUESTO SOBRE LA RENTA</div></td></tr>
                <tr><td><div class="td_company_title"> (DIFERENTES A SUELDOS Y SALARIOS Y DEMÁS REMUNERACIONES SIMILARES A PERSONAS NATURALES RESIDENTES) </div></td></tr>
              </table>
            </td>
          </tr>
        </table>
      %endfor
    </body>
</html>
