import sbol3
import paml

#############################################
# Set up the document
doc = sbol3.Document()
LIBRARY_NAME = 'wait'
sbol3.set_namespace('https://bioprotocols.org/paml/primitives/'+LIBRARY_NAME)

#############################################
# Create the primitives
print('Making primitives for '+LIBRARY_NAME)

p = paml.Primitive('WaitForTime')
p.description = 'Waits for a set amount of time.'
p.add_input('amount', sbol3.OM_MEASURE)
doc.add(p)

p = paml.Primitive('WaitForTrue')
p.description = 'Waits for an expression to be true.'
p.add_input('expression', 'http://www.w3.org/2001/XMLSchema#boolean')
doc.add(p)



print('Library construction complete')

print('Validating library')
for e in doc.validate().errors: print(e);
for w in doc.validate().warnings: print(w);

filename = LIBRARY_NAME+'.ttl'
doc.write(filename,'turtle')
print('Library written as '+filename)
