import os
import tempfile
import sbol3
import paml
import tyto
import uml
import json
import rdflib as rdfl
from typing import Dict

from objexplore import explore

from paml.execution_engine import ExecutionEngine
from paml_check.paml_check import check_doc
from paml_convert.ot2.ot2_specialization import OT2Specialization

# Dev Note: This is a test of the initial version of the OT2 specialization. Any specs shown here can be changed in the future. Use at your own risk. Here be dragons.


#############################################
# set up the document
print('Setting up document')
doc = sbol3.Document()
sbol3.set_namespace('https://bbn.com/scratch/')

#############################################
# Import the primitive libraries
print('Importing libraries')
paml.import_library('liquid_handling')
print('... Imported liquid handling')
paml.import_library('plate_handling')
print('... Imported plate handling')
paml.import_library('spectrophotometry')
print('... Imported spectrophotometry')
paml.import_library('sample_arrays')
print('... Imported sample arrays')


# Example of how to generate a template for a new protocol step

#print(primitives["https://bioprotocols.org/paml/primitives/liquid_handling/Dispense"].template())

protocol = paml.Protocol('iGEM_LUDOX_OD_calibration_2018')
protocol.name = "iGEM 2018 LUDOX OD calibration protocol"
protocol.description = '''
Test Execution
'''
doc.add(protocol)

# create the materials to be provisioned
CONT_NS = rdfl.Namespace('https://sift.net/container-ontology/container-ontology#')
OM_NS = rdfl.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')

PREFIX_MAP = json.dumps({"cont": CONT_NS, "om": OM_NS})


ddh2o = sbol3.Component('ddH2O', 'https://identifiers.org/pubchem.substance:24901740')
ddh2o.name = 'Water, sterile-filtered, BioReagent, suitable for cell culture'
ddh2o.OT2SpecificProps = sbol3.TextProperty(ddh2o,'',0,1)
#indicate where ddh2o is loaded, use JSON to set OT2 Specific parameters; might be cleaner and more pythonesque using a dictionary but this should do for now
#water is in well A1 of reservoir and declaring that the left pipette should be used when pipetting from this reservoir
#since no coordinates were issued its assumed to be loaded into well A1
ddh2o.OT2SpecificProps = '{"deck":"1", "source":"reservoir", "type":"nest_12_reservoir_15ml"}' 
doc.add(ddh2o)

ludox = sbol3.Component('LUDOX', 'https://identifiers.org/pubchem.substance:24866361')
ludox.name = 'LUDOX(R) CL-X colloidal silica, 45 wt. % suspension in H2O'
ludox.OT2SpecificProps = sbol3.TextProperty(ludox,'',0,1)
#indicate where ludox is loaded, use JSON to set OT2 Specific parameters; might be cleaner and more pythonesque using a dictionary but this should do for now
#ludox is in well A2 of reservoir and declaring that the right pipette should be used when pipetting from this reservoir
#no need to redeclare source type as long as it was declared before
ludox.OT2SpecificProps = '{"coordinates":"A2", "source":"reservoir", "pipette":"right"}' 
doc.add(ludox)


# actual steps of the protocol
# get a plate
platespec1 = paml.ContainerSpec(queryString="corning_48_wellplate_1.6ml_flat", prefixMap=PREFIX_MAP, name='plate1')
platespec1.OT2SpecificProps = sbol3.TextProperty(platespec1,"https://bioprotocols.org/paml/primitives/sample_arrays/EmptyContainer/OT2/Deck",0,1)
platespec1.OT2SpecificProps = '{"deck":"2"}'
plate1 = protocol.primitive_step('EmptyContainer', specification=platespec1) # declare a plate loaded in the second deck

platespec2 = paml.ContainerSpec(queryString="corning_48_wellplate_1.6ml_flat", prefixMap=PREFIX_MAP, name='plate2')
platespec2.OT2SpecificProps = sbol3.TextProperty(platespec2,"https://bioprotocols.org/paml/primitives/sample_arrays/EmptyContainer/OT2/Deck",0,1)
platespec2.OT2SpecificProps = '{"deck":"3"}'
plate2 = protocol.primitive_step('EmptyContainer', specification=platespec2) # declare a plate loaded in the third deck

# identify wells to use
c_ddh2o = protocol.primitive_step('PlateCoordinates', source=plate1.output_pin('samples'), coordinates="plate1['A1:D1']")
# put water in selected wells
provision_ddh2o = protocol.primitive_step('Provision', resource=ddh2o, destination=c_ddh2o.output_pin('samples'),amount=sbol3.Measure(100, tyto.OM.microliter))
#identify wells to use
c_ludox = protocol.primitive_step('PlateCoordinates', source=plate1.output_pin('samples'), coordinates="plate1['A2:D2']")
# put ludox in selected wells
provision_ludox = protocol.primitive_step('Provision', resource=ludox, destination=c_ludox.output_pin('samples'),amount=sbol3.Measure(100, tyto.OM.microliter))


# identify wells to use
c_ddh2o2 = protocol.primitive_step('PlateCoordinates', source=plate2.output_pin('samples'), coordinates="plate2['A1:D1']")
# put water in selected wells
provision_ddh2o2 = protocol.primitive_step('Provision', resource=ddh2o, destination=c_ddh2o2.output_pin('samples'),amount=sbol3.Measure(100, tyto.OM.microliter))
#identify wells to use
c_ludox2 = protocol.primitive_step('PlateCoordinates', source=plate2.output_pin('samples'), coordinates="plate2['A2:D2']")
# put ludox in selected wells
provision_ludox2 = protocol.primitive_step('Provision', resource=ludox, destination=c_ludox2.output_pin('samples'),amount=sbol3.Measure(100, tyto.OM.microliter))

transfer_org= protocol.primitive_step('PlateCoordinates', source=plate1.output_pin('samples'), coordinates="plate1['A2']")
transfer_dest= protocol.primitive_step('PlateCoordinates', source=plate2.output_pin('samples'), coordinates="plate2['A2']")
transfer = protocol.primitive_step('Transfer', source=transfer_org.output_pin('samples'), destination=transfer_dest.output_pin('samples'),amount=sbol3.Measure(10, tyto.OM.microliter))

leftTiprackSettingJSON = '{"pipette":"p1000_single_gen2","tipracks":[{"id":"geb_96_tiprack_1000ul","deck":4},{"id":"geb_96_tiprack_1000ul","deck":5}]}'
rightTiprackSettingJSON = '{"pipette":"p20_single_gen2","tipracks":[{"id":"opentrons_96_tiprack_20ul","deck":6},{"id":"opentrons_96_tiprack_20ul","deck":7}]}'

filename="ludox_ot2.py"
agent = sbol3.Agent("test_agent")
ee = ExecutionEngine(specializations=[OT2Specialization("2.11",leftTiprackSettingJSON,rightTiprackSettingJSON)])
parameter_values = []
execution = ee.execute(protocol, agent, id="test_execution")
with open(filename, 'w') as f:
     print(ee.specializations[0].script,file=f)
print(f"All done. Script dumped to {filename}.")

#v = doc.validate()
#assert len(v) == 0, "".join(f'\n {e}' for e in v)

#temp_name = os.path.join(tempfile.gettempdir(), 'ludox.nt')
#doc.write(temp_name, sbol3.SORTED_NTRIPLES)
#print(f'Wrote file as {temp_name}')

 #render and view the dot
#dot = protocol.to_dot()
#dot.render(f'{protocol.name}.gv')
#dot.view()
