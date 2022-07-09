icons = {
	'person':['male','blue'], 
	'quantity':['sort-numeric-asc','yellow'], 
	'time':['clock-o','pink'], 
	'abstract':['cloud','cyan'], 
	'object':['cube','green'], 
	'animal':['paw','orange'], 
	'plant':['pagelines','magenta'], 
	'place':['map-marker','red'], 
	'substance':['flask','purple'], 
	'organization':['bank','brown'], 
	'event':['bell','gold']};

nlp_result = $("#result").html();

if (nlp_result.includes("entity=")){
	nlp_result = nlp_result.replace(/&gt;/g,'>');
	nlp_result = nlp_result.replace(/&lt;/g,'<');
	nlp_result = nlp_result.replace(/&amp;/g,'&');
	nlp_result = nlp_result.replace(/(<|<\/)[^\/e][^<>]+>\n?/g,'');
	nlp_result = nlp_result.replace(/entity=/g,'class="referent" style="border-color: COLOR" entity=');
	nlp_result = nlp_result.replace(/(<\/?)entity/g,'$1div');
	nlp_result = nlp_result.replace(/([^\n<>]+)\n/g,'<span class="entity_tok">$1 </span>');
	formatted = [];
	lines = nlp_result.split("\n");
	icon_template = '<span class="entity_type"><i title="TYPE" class="fa fa-ICON"></i></span>';
	pat = /entity="([^"]+)"/;
	for (line of lines){
		if (line.includes("entity=")){
			e_type = pat.exec(line)[1];
			line += icon_template;
			line = line.replace(/TYPE/,e_type).replace(/ICON/,icons[e_type][0]).replace(/COLOR/,icons[e_type][1]);
		}
		formatted.push(line);
	}
	entity_output = formatted.join("\n");
	$("#entity_container").html(entity_output);
	$("#entity_container").css("display","block");
	$('<p>Entities:</p>').insertBefore( "#entity_container" );
}