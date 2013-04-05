<html xmlns="http://www.w3.org/TR/REC-html40" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">

    <head>
        <title>Planilla de DeclaraciÃ³n/Pago Impuesto al Valor Agregado</title>
        <meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
        <meta content="Word.Document" name="ProgId">
        <meta content="MSHTML 6.00.2726.2500" name="GENERATOR">
        <meta content="Microsoft Word 9" name="Originator">
    </head>

    <body lang="ES">
		  % for vwo in objects :
		<!-- incio encabezado declaracion -->
		  <table width="680" align="center" cellpadding="0" cellspacing="0" border="1">
			<tbody>
				<tr>
					<td width="30%" rowspan="5">
						<img src="http://contribuyente.seniat.gob.ve/imagenes/logo-seniat-int.gif" width="200" height="58" align="middle" border="0">
					</td>
					<td width="40%" align="center">

						FORMA IVA 99030


					</td>
					  <td width="15%" colspan="1" rowspan="1" align="right" valign="middle">No.&nbsp;</td>
					  <td width="15%" colspan="1" rowspan="1" align="right" valign="middle"></span> </td>
					</tr>
					<tr>
					  <td width="40%" align="center">DECLARACION Y PAGO DEL IMPUESTO</td>
					  <td width="15%" colspan="1" align="right" valign="middle">Certificado:&nbsp;</td>
					  <td width="15%" colspan="1" align="right" valign="middle">

					  </span> </td>
					</tr>
					<tr>
					  <td width="40%" align="center">AL VALOR AGREGADO</td>
					  <td width="30%" colspan="2" rowspan="3" align="right" valign="middle">
						<table width="80%" align="right" cellpadding="0" cellspacing="0" border="1">
						  <tbody><tr>
							<td colspan="6" width="100%" align="center"><h4><font size=2>PERIODO DE IMPOSICION: &nbsp ${vwo.period_id.name or ''|entity}</font></h4></td>
						  </tr>
						  <tr>
							<td colspan="2" width="40%" align="center"><h5>MES</h5></td>
							<td colspan="4" width="60%" align="center"><h5>AÑO</h5></td>
						  </tr>
						  <tr>
							<td colspan="2" width="40%" align="center">03</td>
							<td colspan="4" width="60%" align="center">2013</td>
						  </tr>
						</tbody></table>
					  </td>
					</tr>
					<tr>
					  <td width="40%" align="center">&nbsp;</td>
					</tr>
					 <tr>
					  <td width="40%" align="center">&nbsp;</td>
					</tr>

				  </tbody></table>
				  <br>
				  <table width="680" align="center" cellpadding="0" cellspacing="0" border="1">
					<tbody><tr>
					  <td width="80%" align="left"><font size=2>&nbsp;SI ESTA ES UNA DECLARACI&Oacute;N SUSTITUTIVA O COMPLEMENTARIA, &nbsp;N-&nbsp;&nbsp;FECHA&nbsp;</font></td>
					  <td width="20%" align="left">&nbsp;<b><font size=2>FECHA</font></b>&nbsp;

							&nbsp ${vwo.start_date or ''|entity}


					  </td>
					</tr>
					<tr>
					  <td width="80%" align="left">&nbsp;<b><font size=2>A.- DATOS DEL CONTRIBUYENTE</font><b>&nbsp;</b></b></td>
					  <td width="20%" align="left">&nbsp;<b><font size=2>N- RIF</font></b></td>
					</tr>
					<tr>
					  <td width="80%" align="left"><font size=2>&nbsp ${vwo.company_id.name or ''|entity}</font></td>
					  <td width="20%" align="left"><font size=2>&nbsp;${vwo.company_id.vat or ''|entity}&nbsp;</font></td>
					</tr>
				  </tbody></table>
				  <br>
<!--
				  <table width="680" align="center" cellpadding="0" cellspacing="0" border="1">
					<tbody><tr>
					  <td width="100%" colspan="2" align="left">&nbsp;<b>B.- DATOS DEL APODERADO O REPRESENTANTE LEGAL<b>&nbsp;</b></b></td>
					</tr>
					<tr>
					  <td width="80%" align="left">&nbsp;&nbsp;</td>
					  <td width="20%" align="left">&nbsp;<b>Nº RIF</b>&nbsp;</td>
					</tr>
				  </tbody></table>
-->
				  <br>
				<table width="680" align="center" cellpadding="0" cellspacing="0" border="1">
					<tbody><tr>
					  <td bgcolor="#dedede" colspan="2">&nbsp;<strong><font size=2>D&Eacute;BITOS FISCALES</font></strong></td>
					  <td bgcolor="#dedede" colspan="2">&nbsp;<strong><font size=2>BASE IMPONIBLE (BsF)</font></strong></td>
					  <td bgcolor="#dedede" colspan="2">&nbsp;<strong><font size=2>D&Eacute;BITO FISCAL (BsF)</font></strong></td>
				   </tr>
				   <tr>
					  <td align="center">1</td>
					  <td><font size=2>Ventas Internas no Gravadas</font></td>
					  <td align="center"><u>40</u></span></td>
					  <td align="right">
						<input type="text" name="item40" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					  </td>
					  <td colspan="2" rowspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
				   </tr>
				   <tr>
					  <td align="center">2</td>
					  <td><font size=2>Ventas de Exportaci&oacute;n</font></td>
					  <td align="center">41</td>
					  <td align="right">
						<input type="text" name="item41" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					  </td>
				   </tr>
				   <tr>
					<td align="center">3</td>
					<td><font size=2>Ventas Internas Gravadas por Al&iacute;cuota General</font></td>
					<td align="center">42</td>
					<td align="right">
						<input type="text" name="item42" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td align="center">43</td>
					<td align="right">
						<input type="text" name="item43" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td align="center">4</td>
					<td><font size=2>Ventas Internas Gravadas por Al&iacute;cuota General más Alícuota Adicional</font></td>
					<td align="center">442</td>
					<td align="right">
						<input type="text" name="item442" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td align="center">452</td>
					<td align="right">
						<input type="text" name="item452" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td align="center">5</td>
					<td><font size=2>Ventas Internas Gravadas por Al&iacute;cuota Reducida&nbsp;</font></td>
					<td align="center">443</td>
					<td align="right">
						<input type="text" name="item443" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td align="center">453</td>
					<td align="right">
					  <input type="text" name="item453" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td align="center" width="4%">6</td>
					<td width="67%"><font size=2>Total Ventas y D&eacute;bitos Fiscal para efectos de Determinación</font></td>
					<td align="center" width="4%">46</td>
					<td align="right" width="15%">
						<input type="text" name="item46" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td align="center" width="4%">47</td>
					<td align="right" width="15%">
						<input type="text" name="item47" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td align="center">7</td>
					<td colspan="3"><font size=2>Ajustes a los D&eacute;bitos Fiscales de per&iacute;odos anteriores</font></td>
					<td align="center">48</td>
					<td align="right">
					  <input type="text" name="item48" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td align="center">8</td>
					<td colspan="3"><font size=2>Certificados de D&eacute;bitos Fiscales Exonerados (recibos de entes exonerados). Registro del Per&iacute;odo </font></td>
					<td align="center">80</td>
					<td align="right">
						  <input type="text" name="item80" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td width="4%" height="20" align="center">9</td>
					<td colspan="3" width="67%"><strong><font size=2>Total D&eacute;bitos Fiscales </font></strong></td>
					<td align="center" width="4%">49</td>
					<td align="right" width="15%">
						<input type="text" name="item49" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				  <tr>
					<td colspan="2" bgcolor="#dedede">&nbsp;<strong><font size=2>CR&Eacute;DITOS FISCALES</font></strong></td>
					<td colspan="2" bgcolor="#dedede">&nbsp;<strong><font size=2>BASE IMPONIBLE (BsF)</font></strong></td>
					<td colspan="2" bgcolor="#dedede">&nbsp;<strong><font size=2>CR&Eacute;DITO FISCAL (BsF)</font></strong></td>
				 </tr>
				 <tr>
					<td align="center">10</td>
					<td><font size=2>Compras no Gravadas y/o sin Derecho a Cr&eacute;dito Fiscal</font></td>
					<td align="center">30</td>
					<td align="right">
						<input type="text" name="item30" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td colspan="2" align="center" bgcolor="#dedede">&nbsp;</td>
				 </tr>
				 <tr>
					<td width="4%" align="center">11</td>
					<td width="67%"><font size=2>Importaci&oacute;n Gravadas por Al&iacute;cuota General</font></td>
					<td width="4%" align="center">31</td>
					<td width="15%" align="right">
						  <input type="text" name="item31" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td width="4%" align="center">32</td>
					<td width="15%" align="right">
						  <input type="text" name="item32" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td align="center">12</td>
					<td><font size=2>Importaciones Gravadas por Al&iacute;cuota General más Al&iacute;cuota Adicional</font></td>
					<td align="center">312</td>
					<td align="right">
						  <input type="text" name="item312" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td align="center">322</td>
					<td align="right">
						  <input type="text" name="item322" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td align="center">13</td>
					<td><font size=2>Importaciones Gravadas por Al&iacute;cuota Reducida</font></td>
					<td align="center">313</td>
					<td align="right">
						<input type="text" name="item313" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td align="center">323</td>
					<td align="right">
						<input type="text" name="item323" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td align="center">14</td>
					<td><font size=2>Compras Internas Gravadas  por Al&iacute;cuota General</font></td>
					<td align="center">33</td>
					<td align="right">
						<input type="text" name="item33" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td align="center">34</td>
					<td align="right">
						<input type="text" name="item34" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
				 <tr>
					<td align="center">15</td>
					<td><font size=2>Compras Internas Gravadas  por Al&iacute;cuota General más Al&iacute;cuota Adicional</font></td>
					<td align="center">332</td>
					<td align="right">
						<input type="text" name="item332" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
					<td align="center">342</td>
					<td align="right">
						<input type="text" name="item342" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				 </tr>
		   <tr>
			  <td align="center">16</td>
			  <td><font size=2>Compras Internas Gravadas por Al&iacute;cuota Reducida</font></td>
			  <td align="center">333</td>
			  <td align="right">
				  <input type="text" name="item333" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td align="center">343</td>
			  <td align="right">
				  <input type="text" name="item343" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">17</td>
			  <td><font size=2>Total Compras y Cr&eacute;ditos Fiscales del Per&iacute;odo</font></td>
			  <td align="center">35</td>
			  <td align="right" style="border-bottom: #666666 solid 1px;border-right: #666666 solid 1px;">
				  <input type="text" name="item35" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td align="center">36</td>
			  <td align="right">
				  <input type="text" name="item36" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">18</td>
			  <td colspan="3"><font size=2>Cr&eacute;ditos Fiscales Totalmente Deducibles</font></td>
			  <td align="center">70</td>
			  <td align="right">
				  <input type="text" name="item70" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">19</td>
			  <td colspan="3"><font size=2>Cr&eacute;ditos Fiscales producto de la Aplicaci&oacute;n del porcentaje de la prorrata</font></td>
			  <td align="center">37</td>
			  <td align="right">
				  <input type="text" name="item37" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">20</td>
		   <td colspan="3"><font size=2>Total cr&eacute;ditos fiscales deducibles... Realice la operaci&oacute;n (70 + 37)</font></td>
			  <td align="center">71</td>
			  <td align="right">
				  <input type="text" name="item71" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">21</td>
			  <td colspan="3"><font size=2>Excedente Cr&eacute;ditos Fiscales del mes Anterior (&iacute;tem 60 de la declaraci&oacute;n anterior)</font></td>
			  <td align="center">20</td>
			  <td align="right">
				  <input type="text" name="item20" value="11.146,08" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">22</td>
			  <td colspan="3"><font size=2>Reintegro Solicitado (s&oacute;lo Exportadores)</font></td>
			  <td align="center">21</td>
			  <td align="right">
				  <input type="text" name="item21" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">23</td>
			  <td colspan="3"><font size=2>Reintegro Solicitado (s&oacute;lo quien suministre bienes o presten servicios a entes exonerados)</font></td>
			  <td align="center">81</td>
			  <td align="right">
				  <input type="text" name="item81" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">24</td>
			  <td colspan="3"><font size=2>Ajustes a los Cr&eacute;ditos Fiscales de per&iacute;odos anteriores</font></td>
			  <td align="center">38</td>
			  <td align="right">
				  <input type="text" name="item38" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">25</td>
			  <td colspan="3"><font size=2>Certificados de D&eacute;bitos Fiscales Exonerados (emitidos por entes exonerados) . Registrado en el per&iacute;odo</font></td>
			  <td align="center">82</td>
			  <td align="right">
				  <input type="text" name="item82" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
				 <tr>
					<td align="center">26</td>
					<td colspan="3"><strong><font size=2>Total Cr&eacute;ditos Fiscales</font></strong></td>
					<td align="center">39</td>
					<td align="right" width="15%">
						<input type="text" name="item39" value="11.146,08" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
				  </td>
				 </tr>
				  <tr>
					  <td colspan="6" bgcolor="#dedede" align="left">&nbsp;<strong><font size=2>AUTOLIQUIDACI&Oacute;N (BsF)</font></strong>
					  </td>
				   </tr>
				   <tr>
					<td align="center" width="4%">27</td>
					<td colspan="3" width="67%"><font size=2>Total Cuota Tributaria del Per&iacute;odo</font></td>
					<td align="center" width="4%">53</td>
					<td align="right" width="15%">
				  <input type="text" name="item53" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				  </tr>
				  <tr>
					<td align="center" width="4%">28</td>
					<td colspan="3" width="67%"><font size=2>Excedente de Cr&eacute;dito Fiscal para el mes siguiente</font></td>
					<td align="center" width="4%">60</td>
					<td align="right" width="15%">
						<input type="text" name="item60" value="11.146,08" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					</td>
				   </tr>
				   <tr>
					  <td align="center">29</td>
					  <td><font size=2>Impuesto pagado en Declaraci&oacute;n(es) Sustituida(s)</font></td>
					  <td align="center">22</td>
					  <td align="right">
						<input type="text" name="item22" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
					  </td>
					  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
				  </tr>
		   <tr>
			  <td align="center">30</td>
			  <td><font size=2>Retenciones Descontadas en Declaraci&oacute;n(es) Sustituida(s)</font></td>
			  <td align="center">51</td>
			  <td align="right">
				  <input type="text" name="item51" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center">31</td>
			  <td><font size=2>Percepciones Descontadas en Declaraci&oacute;n(es) Sustituida(s)</font></td>
			  <td align="center">24</td>
			  <td align="right">
					<input type="text" name="item24" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center" width="4%">32</td>
			  <td colspan="3" width="67%"><font size=2>Sub-total Impuesto a Pagar</font></td>
			  <td align="center" width="4%">78</td>
			  <td align="right" width="15%">
				  <input type="text" name="item78" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">33</td>
			  <td><font size=2>Retenciones Acumuladas por Descontar</font></td>
			  <td align="center">54</td>
			  <td align="right">
				  <input type="text" name="item54" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center">34</td>
			  <td><font size=2>Retenciones del Per&iacute;odo</font></td>
			  <td align="center">66</td>
			  <td align="right">
				  <input type="text" name="item66" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp; </td>
		   </tr>
		   <tr>
			  <td align="center">35</td>
			  <td><font size=2>Créditos Adquiridos por Cesi&oacute;n de Retenciones</font></td>
			  <td align="center">72</td>
			  <td align="right">
				  <input type="text" name="item72" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center">36</td>
			  <td><font size=2>Recuperaci&oacute;n de Retenciones Solicitado (saldo con antigüedad mayor a dos períodos impositivos) </font></td>
			  <td align="center">73</td>
			  <td align="right">
				  <input type="text" name="item73" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center">37</td>
			  <td><font size=2>Total Retenciones</font></td>
			  <td align="center">74</td>
			  <td align="right">
				  <input type="text" name="item74" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center" width="4%">38</td>
			  <td colspan="3" width="67%"><font size=2>Retenciones Soportadas y Descontadas en esta Declaraci&oacute;n</font></td>
			  <td align="center" width="4%">55</td>
			  <td align="right" width="15%">
				  <input type="text" name="item55" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">39</td>
			  <td><font size=2>Saldo de Retenciones de IVA no aplicado </font></td>
			  <td align="center">67</td>
			  <td align="right">
				  <input type="text" name="item67" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center" width="4%">40</td>
			  <td colspan="3" width="67%"><font size=2>Sub-total Impuesto a Pagar</font></td>
			  <td align="center" width="4%">56</td>
			  <td align="right" width="15%">
				  <input type="text" name="item56" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">41</td>
			  <td><font size=2>Percepciones Acumuladas en Importaciones por Descontar</font></td>
			  <td align="center">57</td>
			  <td align="right">
				  <input type="text" name="item57" value="" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center">42</td>
			  <td><font size=2>Percepciones del Per&iacute;odo</font></td>
			  <td align="center">68</td>
			  <td align="right">
				  <input type="text" name="item68" value="" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center">43</td>
			  <td><font size=2>Créditos Adquiridos por Cesi&oacute;n de Percepciones </font></td>
			  <td align="center">75</td>
			  <td align="right">
				  <input type="text" name="item75" value="" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center">44</td>
			  <td><font size=2>Recuperaci&oacute;n de Percepciones Solicitado (saldo con antigüedad mayor a dos períodos impositivos) </font></td>
			  <td align="center">76</td>
			  <td align="right">
				  <input type="text" name="item76" value="" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center">45</td>
			  <td><font size=2>Total Percepciones</font></td>
			  <td align="center">77</td>
			  <td align="right">
				  <input type="text" name="item77" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center" width="4%">46</td>
			  <td colspan="3" width="67%"><font size=2>Percepciones en Aduanas Descontadas en esta Declaraci&oacute;n </font></td>
			  <td align="center" width="4%">58</td>
			  <td align="right" width="15%">
				  <input type="text" name="item58" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
		   </tr>
		   <tr>
			  <td align="center">47</td>
			  <td><font size=2>Saldo de Percepciones en Aduanas no Aplicado </font></td>
			  <td align="center">69</td>
			  <td align="right">
				  <input type="text" name="item69" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			  </td>
			  <td colspan="2" align="center" bgcolor="#dedede" style="border-bottom: #666666 solid 1px;border-right: #666666 solid 1px;">&nbsp;</td>
		   </tr>
		   <tr>
			  <td align="center" width="4%">48</td>
		 <td colspan="3" width="67%"><strong><font size=2>Total a Pagar</font></strong></td>
		 <td align="center" width="4%">90</td>
		 <td align="right" width="15%">
				  <input type="text" name="item90" value="0" onkeypress="bloquear('soloNumeros');" onfocus="blur();" tabindex="1">
			</td>
		   </tr>
		   </tbody></table>
	  % endfor
   </body>
</html>
