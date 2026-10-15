from tool_diff import compare
old={'tools':[{'name':'fixture_lookup','description':'Read fixture','inputSchema':{'type':'object'}}]}
new={'tools':[{'name':'fixture_lookup','description':'Changed fixture behavior','inputSchema':{'type':'object'}}]}
r=compare(old,new)
assert r['review_required'] and r['changed'][0]['fields']==['description']
print('REVIEW: fixture_lookup description changed')
assert not compare(old,old)['review_required']
print('UNCHANGED: identical inventory has no drift')
print('No server contacted or tool executed')
