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
                <div>${helper.embed_image('jpeg',str(obj.islr_wh_doc_id.company_id.logo),260, 120)}</div>
                <div>RIF: ${obj.islr_wh_doc_id.company_id.partner_id.vat[2:]|entity}</div>
            </td>
            <td>
              <table style="width: 100%; text-align:center;">
                <tr><td><div class="td_company_title">${obj.islr_wh_doc_id.company_id.name or ''|entity}</div></td></tr>
              </table>
            </td>
          </tr>
        </table>
        <br clear="all"/>
        <em>
            <div>
            </div>
        </em>
        <table class="list_table"  width="100%" border="0">
            <thead>
                <tr>
                    <th class="celdaTituloTabla" width="100%">[${obj.invoice_id.partner_id.vat and obj.invoice_id.partner_id.vat[2:] or 'FALTA RIF'|entity}] ${obj.invoice_id.partner_id.name or ''|entity} </th>
                </tr>
            </thead>
        </table>
        <em>
            <div>
                <p>
Adjunto reciban Vds. ${u'%s'%(obj.reference or u'NO HAY REFERENCIA') | entity} relacionado con esta orden de Pago de ${obj.journal_id.name.upper()} resultante de la transacción efectuada el ${formatLang(obj.date, digits=2, date=True, date_time=False, grouping=3, monetary=False)} por la cantidad de ${obj.currency_id.symbol} (${obj.currency_id.name}) ${formatLang(obj.amount, digits=2, date=False, date_time=False, grouping=3, monetary=True)} para la liquidación de las siguientes partidas:
                </p>
            </div>
        </em>
        <%
            untaxed = tax = total = vat = islr = muni = pay = residual = 0.0
        %>
        <table class="list_table"  width="100%" border="0">
            <tbody>
                <%
                    avl_brws, inv_brws = obj.get_invoices()
                %>
                %if inv_brws:
                    <tr class="prueba">
                        <td class="celdaTituloTabla" width="10%">
                            FACTURAS
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                    </tr>
                    <tr class="prueba" >
                        <td class="celdaTotalTitulo" width="10%">
                            DOC.
                        </td>
                        <td class="celdaTotal" width="9%">
                            F/EMISION
                        </td>
                        <td class="celdaTotal" width="9%">
                            BASE IMP.
                        </td>
                        <td class="celdaTotal" width="9%">
                            IMP.
                        </td>
                        <td class="celdaTotal" width="9%">
                            TOT/FACT.
                        </td>
                        <td class="celdaTotal" width="9%">
                            RET/IVA
                        </td>
                        <td class="celdaTotal" width="9%">
                            RET/ISLR
                        </td>
                        <td class="celdaTotal" width="9%">
                            TIMB/FISC.
                        </td>
                        <td class="celdaTotal" width="9%">
                            ABONOS
                        </td>
                        <td class="celdaTotal" width="9%">
                            SALDO
                        </td>
                        <td class="celdaTotal" width="9%">
                            IMPORTE
                        </td>
                    </tr>
                    %for inv_brw, avl_brw in inv_brws:
                        <%
                        inv_vals = obj.get_invoice_payments(inv_brw, avl_brw)
                        inv_vals['payment'] = (inv_vals['payment'] - avl_brw.amount) if obj.state=='posted' else inv_vals['payment']
                        untaxed += inv_brw.amount_untaxed
                        tax += inv_brw.amount_tax
                        total += inv_brw.amount_total
                        vat -= inv_vals['wh_vat']
                        islr -= inv_vals['wh_islr']
                        muni -= inv_vals['wh_muni']
                        pay -= inv_vals['payment']
                        residual += avl_brw.amount_unreconciled
                        %>
                        <tr class="prueba">
                            <td class="celdaDetailTitulo" width="10%"> ${inv_brw.supplier_invoice_number.upper()} </td>
                            <td class="celdaDetail" width="9%"> ${inv_brw.date_document and formatLang(inv_brw.date_document, digits=2, date=True, date_time=False, grouping=3, monetary=False) or 'CORREGIR'} </td>
                            <td class="celdaDetail" width="9%"> ${formatLang(inv_brw.amount_untaxed, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                            <td class="celdaDetail" width="9%"> ${formatLang(inv_brw.amount_tax, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                            <td class="celdaDetail" width="9%"> ${formatLang(inv_brw.amount_total, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                            <td class="celdaDetail" width="9%"> ${inv_vals['wh_vat'] and formatLang(-1*inv_vals['wh_vat'], digits=2, date=False, date_time=False, grouping=3, monetary=True) or formatLang(inv_vals['wh_vat'], digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                            <td class="celdaDetail" width="9%"> ${inv_vals['wh_islr'] and formatLang(-1*inv_vals['wh_islr'], digits=2, date=False, date_time=False, grouping=3, monetary=True) or formatLang(inv_vals['wh_islr'], digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                            <td class="celdaDetail" width="9%"> ${inv_vals['wh_muni'] and formatLang(-1*inv_vals['wh_muni'], digits=2, date=False, date_time=False, grouping=3, monetary=True) or formatLang(inv_vals['wh_muni'], digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                            <td class="celdaDetail" width="9%"> ${inv_vals['payment'] and formatLang(-1*inv_vals['payment'], digits=2, date=False, date_time=False, grouping=3, monetary=True) or formatLang(inv_vals['payment'], digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                            <td class="celdaDetail" width="9%"> ${formatLang(avl_brw.amount_unreconciled, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                            <td class="celdaDetail" width="9%"> ${formatLang(avl_brw.amount, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                        </tr>
                    %endfor
                %endif
            </tbody>
        </table>
        <table class="list_table"  width="100%" border="0">
            <tbody>
                <%
                    avl_brws, inv_brws = obj.get_invoices()
                %>
                %if avl_brws:
                    <tr class="prueba">
                        <td class="celdaTituloTabla" width="82%">
                            DÉBITOS
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                    </tr>
                    <tr class="prueba" >
                        <td class="celdaTotalTitulo" width="82%">
                            REFERENCIA
                        </td>
                        <td class="celdaTotal" width="9%">
                            SALDO
                        </td>
                        <td class="celdaTotal" width="9%">
                            IMPORTE
                        </td>
                    </tr>
                    %for avl_brw in avl_brws:
                        <%
                            residual += avl_brw.amount_unreconciled
                        %>
                        <tr class="prueba" >
                            <td class="celdaDetailTitulo" width="82%">
                                ${u'%s - %s'%(avl_brw.move_line_id and avl_brw.move_line_id.name.upper() or '/', avl_brw.move_line_id and avl_brw.move_line_id.ref.upper() or '/')}
                            </td>
                            <td class="celdaDetail" width="9%">
                                ${formatLang(avl_brw.amount_unreconciled, digits=2, date=False, date_time=False, grouping=3, monetary=True)}
                            </td>
                            <td class="celdaDetail" width="9%">
                                ${formatLang(avl_brw.amount, digits=2, date=False, date_time=False, grouping=3, monetary=True)}
                            </td>
                        </tr>
                    %endfor
                %endif
            </tbody>
        </table>
        <table class="list_table"  width="100%" border="0">
            <tbody>
                <%
                    avl_brws = obj.line_cr_ids
                %>
                %if avl_brws:
                    <tr class="prueba">
                        <td class="celdaTituloTabla" width="82%">
                            CRÉDITOS
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                    </tr>
                    <tr class="prueba" >
                        <td class="celdaTotalTitulo" width="82%">
                            REFERENCIA
                        </td>
                        <td class="celdaTotal" width="9%">
                        </td>
                        <td class="celdaTotal" width="9%">
                            IMPORTE
                        </td>
                    </tr>
                    %for avl_brw in avl_brws:
                        <%
                            residual -= avl_brw.amount_unreconciled
                        %>
                        <tr class="prueba" >
                            <td class="celdaDetailTitulo" width="82%">
                                ${avl_brw.move_line_id.name.upper()}
                            </td>
                            <td class="celdaDetail" width="9%">
                            </td>
                            <td class="celdaDetail" width="9%">
                                ${formatLang(-1 * avl_brw.amount, digits=2, date=False, date_time=False, grouping=3, monetary=True)}
                            </td>
                        </tr>
                    %endfor
                %endif
            </tbody>
        </table>
        %if obj.writeoff_amount:
            <table class="list_table"  width="100%" border="0">
                <tbody>
                    <tr class="prueba">
                        <td class="celdaTituloTabla" width="91%">
                            ANTICIPO
                        </td>
                        <td class="celdaTituloTabla" width="9%">
                        </td>
                    </tr>
                    <tr class="prueba" >
                        <td class="celdaDetailTitulo" width="10%">
                            MONTO ANTICIPADO
                        </td>
                        <td class="celdaDetail" width="9%"> 
                            ${formatLang(obj.writeoff_amount, digits=2, date=False, date_time=False, grouping=3, monetary=True)} 
                        </td>
                    </tr>
                </tbody>
            </table>
        %endif
        <table class="list_table"  width="100%" border="0">
            <thead>
                <tr>
                    <th class="celdaTituloTabla" width="82%">TOTAL PAGO NETO</th>
                    <th class="celdaTituloTabla" width="18%"> ${formatLang(obj.amount, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </th>
                </tr>
            </thead>
        </table>
        <table class="list_table"  width="100%" border="0">
            <tbody>
                <tr class="prueba" >
                    <td class="celdaTotalTitulo" width="19%">
                    </td>
                    <td class="celdaTotal" width="9%">
                        BASE IMP.
                    </td>
                    <td class="celdaTotal" width="9%">
                        IMP.
                    </td>
                    <td class="celdaTotal" width="9%">
                        TOT/FACT.
                    </td>
                    <td class="celdaTotal" width="9%">
                        RET/IVA
                    </td>
                    <td class="celdaTotal" width="9%">
                        RET/ISLR
                    </td>
                    <td class="celdaTotal" width="9%">
                        TIMB/FISC.
                    </td>
                    <td class="celdaTotal" width="9%">
                        ABONOS
                    </td>
                    <td class="celdaTotal" width="9%">
                        SALDO
                    </td>
                    <td class="celdaTotal" width="9%">
                        IMPORTE
                    </td>
                </tr>
                <tr class="prueba">
                    <td class="celdaDetailTitulo" width="19%"> </td>
                    <td class="celdaDetail" width="9%"> ${formatLang(untaxed, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                    <td class="celdaDetail" width="9%"> ${formatLang(tax, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                    <td class="celdaDetail" width="9%"> ${formatLang(total, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                    <td class="celdaDetail" width="9%"> ${vat and formatLang(vat, digits=2, date=False, date_time=False, grouping=3, monetary=True) or formatLang(vat, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                    <td class="celdaDetail" width="9%"> ${islr and formatLang(islr, digits=2, date=False, date_time=False, grouping=3, monetary=True) or formatLang(islr, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                    <td class="celdaDetail" width="9%"> ${muni and formatLang(muni, digits=2, date=False, date_time=False, grouping=3, monetary=True) or formatLang(muni, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                    <td class="celdaDetail" width="9%"> ${pay and formatLang(pay, digits=2, date=False, date_time=False, grouping=3, monetary=True) or formatLang(pay, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                    <td class="celdaDetail" width="9%"> ${formatLang(residual, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                    <td class="celdaDetail" width="9%"> ${formatLang(obj.amount, digits=2, date=False, date_time=False, grouping=3, monetary=True)} </td>
                </tr>
            </tbody>
        </table>
        <em>
            <div>
                <pre class="CUSTOMERTEXT">Otras Notas: </pre>
                <p> ${obj.narration and obj.narration or 'Sin Comentarios'| entity} </p>
            </div>
        </em>
        <table class="list_table"  width="100%" border="0">
            <tbody>
                <tr class="prueba">
                    <td class="celdaTituloTabla" width="32%">
                        PETICIONADO POR
                    </td>
                    <td class="celdaTituloTabla" width="50%">
                        DEPARTAMENTO
                    </td>
                    <td class="celdaTituloTabla" width="9%">
                        MONEDA
                    </td>
                    <td class="celdaTituloTabla" width="9%">
                        CANTIDAD
                    </td>
                </tr>
                <tr class="prueba" >
                    <td class="celdaDetailTitulo" width="32%">
                        ${obj.auth_requester_employee_id.name}
                    </td>
                    <td class="celdaDetailTitulo" width="50%">
                        ${obj.auth_requester_dept_id.name}
                    </td>
                    <td class="celdaDetail" width="9%">
                        ${obj.auth_currency_id.name}
                    </td>
                    <td class="celdaDetail" width="9%">
                        ${formatLang(obj.auth_amount, digits=2, date=False, date_time=False, grouping=3, monetary=True)} 
                    </td>
                </tr>
            </tbody>
        </table>
        <%
            apl_approved = [apl_brw for apl_brw in obj.apl_ids if apl_brw.auth_state=='approved']
            apl_waiting = [apl_brw for apl_brw in obj.apl_ids if apl_brw.auth_state=='waiting']
        %>
        %if apl_approved:
            <table class="list_table"  width="100%" border="0">
                <tbody>
                    <tr class="prueba">
                        <td class="celdaTituloTabla" width="100%">
                            AUTORIZACIONES CONCEDIDAS
                        </td>
                    </tr>
                </tbody>
            </table>
            <table class="list_table"  width="100%" border="0">
                <tbody>
                    <tr class="prueba">
                        <td class="celdaTotalTitulo" width="24.5%">
                            AUTORIDAD
                        </td>
                        <td class="celdaTotalTitulo" width="15%">
                            NIVEL
                        </td>
                        <td class="celdaTotalTitulo" width="33.5%">
                            DEPARTAMENTO
                        </td>
                        <td class="celdaTotalTitulo" width="18%">
                            AUTORIZACIÓN
                        </td>
                        <td class="celdaTotalTitulo" width="9%">
                            FEC/AUT.
                        </td>
                    </tr>
                    %for apl_brw in apl_approved:
                        <tr class="prueba" >
                            <td class="celdaDetailTitulo" width="24.5%">
                                ${apl_brw.auth_employee_id.name}
                            </td>
                            <td class="celdaDetailTitulo" width="15%">
                                ${apl_brw.auth_level_id.name}
                            </td>
                            <td class="celdaDetailTitulo" width="33.5%">
                                ${apl_brw.auth_department_id.name}
                            </td>
                            <td class="celdaDetailTitulo" width="18%">
                                APROBADO
                            </td>
                            <td class="celdaDetailTitulo" width="9%">
                                ${formatLang(apl_brw.date_auth, digits=2, date=True, date_time=False, grouping=3, monetary=False)}
                            </td>
                        </tr>
                    %endfor
                </tbody>
            </table>
        %endif
        %if apl_waiting:
            <table class="list_table"  width="100%" border="0">
                <tbody>
                    <tr class="prueba">
                        <td class="celdaTituloTabla" width="100%">
                            AUTORIZACIONES PENDIENTES 
                        </td>
                    </tr>
                </tbody>
            </table>
            <table class="list_table"  width="100%" border="0">
                <tbody>
                    <tr class="prueba">
                        <td class="celdaTotalTitulo" width="24.5%">
                            AUTORIDAD
                        </td>
                        <td class="celdaTotalTitulo" width="15%">
                            NIVEL
                        </td>
                        <td class="celdaTotalTitulo" width="33.5%">
                            DEPARTAMENTO
                        </td>
                        <td class="celdaTotalTitulo" width="18%">
                            AUTORIZACIÓN
                        </td>
                        <td class="celdaTotalTitulo" width="9%">
                            FEC/AUT.
                        </td>
                    </tr>
                    %for apl_brw in apl_waiting:
                        <tr class="prueba" >
                            <td class="celdaDetailTitulo" width="24.5%">
                                ${apl_brw.auth_employee_id.name}
                            </td>
                            <td class="celdaDetailTitulo" width="15%">
                                ${apl_brw.auth_level_id.name}
                            </td>
                            <td class="celdaDetailTitulo" width="33.5%">
                                ${apl_brw.auth_department_id.name}
                            </td>
                            <td class="celdaDetailTitulo" width="18%">
                                EN ESPERA
                            </td>
                            <td class="celdaDetailTitulo" width="9%">
                            </td>
                        </tr>
                    %endfor
                </tbody>
            </table>
        %endif
        %if not (apl_waiting + apl_approved):
            <table class="list_table"  width="100%" border="0">
                <tbody>
                    <tr class="prueba">
                        <td class="celdaTituloTabla" width="100%">
                            DOCUMENTO SIN AUTORIZACIONES
                        </td>
                    </tr>
                </tbody>
            </table>
            <em>
                <div>
                    <p>Este documento debe pasar por un proceso de autorizaciones antes de poder ser empleado en el ámbito fuera de CICSA </p>
                </div>
            </em>
        %endif
        <table class="list_table"  width="100%" border="0">
            <tbody>
                <tr class="prueba">
                    <td class="celdaTituloTabla" width="100%">
                        RECEPCIÓN DE CONFORMIDAD
                    </td>
                </tr>
            </tbody>
        </table>
        <table class="list_table"  width="100%" border="0">
            <tbody>
                <tr class="prueba">
                    <td class="celdaTotalTitulo" width="24.5%">
                        [${obj.invoice_id.partner_id.vat and obj.invoice_id.partner_id.vat[2:] or 'FALTA RIF'|entity}] ${obj.invoice_id.partner_id.name or ''|entity}
                    </td>
                </tr>
                <tr class="prueba" >
                    <td class="celdaDetailTitulo" width="24.5%">
                        RECIBE CONFORME:
                    </td>
                </tr>
            </tbody>
        </table>
      %endfor
    </body>
</html>
