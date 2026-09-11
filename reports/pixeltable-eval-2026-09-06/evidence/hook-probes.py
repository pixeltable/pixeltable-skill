import importlib.util, json, pathlib, tempfile
root=pathlib.Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('hook', root/'hooks/validate_antipatterns.py')
hook=importlib.util.module_from_spec(spec); spec.loader.exec_module(hook)
probes={
 'valid_keyword_similarity':'result = t.text.similarity(string=query)',
 'invalid_positional_similarity':'result = t.text.similarity(query)',
 'comment_false_positive':'# Do not use t.text.similarity(query)',
 'string_false_positive':'message = "Do not use t.text.similarity(query)"',
 'unrelated_class_false_positive':'class FrameIterator: pass',
 'unrelated_dict_false_positive':'result = response["request_errormsg"]',
 'app_full_write':'TableModel = pxt.model_base()\nt.add_embedding_index("text", embedding=fn)',
 'app_edit_fragment':'t.add_embedding_index("text", embedding=fn)',
 'multiline_import_false_negative':'from pixeltable.functions.openai import (\n    vision,\n)',
 'keyword_then_positional_false_negative':'result = t.text.similarity(idx="my_idx", *[query])',
 'ordinary_framework_false_positive':'import langchain\n# Unrelated project; no Pixeltable imports.',
}
results={name:hook.findings_for(code) for name,code in probes.items()}
print(json.dumps({'probes':probes,'results':results}, indent=2))
