<hmtl>    
 <body>
   % for vwo in objects :
       <table cellspacing="10" cellpadding="15" border="3">
            <tr>
                <td width="30%" align="left">LOGO_SENIAT</td>
                <td width="40%" align="center">DECLARACION DEL IMPUESTO AL VALOR AGREGADO FORMA 30</td>
                <td width="30%" align="center">
                    <table cellspacing="2" cellpadding="2" border="1">
                        <tr>
                            <td width="20%" align="left">N.-</td>
                            <td width="20%" align="left">PERIODO DE IMPOSICION:${vwo.period_id.name or ''|entity}</td>
                        </tr>
                        <tr>
                            <td>MES:</td>
                            <td>A#O:</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        <table>
            <tr>
                <td>Razon Social:${vwo.company_id.name or ''|entity}</td>
                <td>N. de Rif:${vwo.company_id.vat or ''|entity}</td>
            </tr>
            <tr>
                <td>Direccion o domicilio fiscal:${vwo.company_id.street or ''|entity}</td>
            </tr>
            <tr>
                <td><font face="Comic Sans MS,arial,verdana" size=4>En caso de sustitutiva:</font> 
                </td>
                <td><font face="Comic Sans MS,arial,verdana">N.- de Declaracion Anterior:</font>

                </td>
                <td><font face="Comic Sans MS,arial,verdana">Fecha:${vwo.start_date or ''|entity}</font>

                </td>
            </tr>
        </table>
        <table>
            <tr>
                <td>
                    <th colspan="4" width="60%">DEBITOS FISCALES</th>
                </td>
                <td>
                    <th colspan="4" width="20%">BASE IMPONIBLE</th>
                </td>
                <td>
                    <th colspan="4" width="20%">DEBITO FISCAL</th>
                </td>
            </tr>
            <tr>
                <td></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td>
                    <th colspan="4" width="60%">CREDITOS FISCALES</th>
                </td>
                <td>
                    <th colspan="4" width="20%">BASE IMPONIBLE</th>
                </td>
                <td>
                    <th colspan="4" width="20%">DEBITO FISCAL</th>
                </td>
            </tr>
            <tr>
                <td></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td>
                    <th colspan="4" width="60%">AUTOLIQUIDACION/BASADO EN UNA SUSTITUTIVA</th>
                </td>
            </tr>
            <tr>
                <td></td>
                <td></td>
                <td></td>
            </tr>
        </table>
        <table>
            <tr>
                <td>
                    <th colspan="4" width="20%">CODIGO N.-</th>
                </td>
                <td>
                    <th colspan="4" width="60%">DESCRIPCION DEL CODIGO-PLAN UNICO DE CUENTAS</th>
                </td>
                <td>
                    <th colspan="4" width="20%">MONTO EN Bs</th>
                </td>
            </tr>
            <tr>
                <td></td>
                <td></td>
                <td></td>
            </tr>
            <tr>
                <td>
                    <th colspan="4" width="50%">Ciudad o Lugar</th>
                </td>
                <td>
                    <th colspan="4" width="50%">Firma del Representante Legal</th>
                </td>
            </tr>
            <tr>
                <td></td>
                <td></td>
                <td></td>
            </tr>
        </table>
      % endfor
    </body>    
</html>
