$.when($.getScript("script/raphael.js"), $.getScript("script/arborator.draw.js"), $.getScript("script/q_nlp.js")).done(function() {
	alert("ok");
});