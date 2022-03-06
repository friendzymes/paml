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

protocol = paml.Protocol('ASFV_qPCR_MM_Preparation')
protocol.name = "ASFV qPCR Master Mix Preparation Template"
protocol.description = '''
ver6
'''
doc.add(protocol)

# create the materials to be provisioned
CONT_NS = rdfl.Namespace('https://sift.net/container-ontology/container-ontology#')
OM_NS = rdfl.Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
PREFIX_MAP = json.dumps({"cont": CONT_NS, "om": OM_NS})
ul_per_s=sbol3.UnitDivision('microliter_per_second','uL/s','microliter_per_second',tyto.OM.microliter,tyto.OM.second)


nfw = sbol3.Component('nfw', 'https://pgc.up.edu.ph/temp/nfw')
nfw.name = 'Invitrogen Nuclease-Free Water'
nfw.OT2SpecificProps = sbol3.TextProperty(nfw,'',0,1)
nfw.OT2SpecificProps = '{"coordinates":"A5","deck":"5", "source":"reservoir", "type":"opentrons_24_aluminumblock_generic_2ml_screwcap"}' 
doc.add(nfw)

primerf = sbol3.Component('primerf', 'https://pgc.up.edu.ph/temp/primerf')
primerf.name = 'ASFV-Primer F'
primerf.OT2SpecificProps = sbol3.TextProperty(primerf,'',0,1)
primerf.OT2SpecificProps = '{"coordinates":"C5", "source":"reservoir"}' 
doc.add(primerf)

primerr = sbol3.Component('primerr', 'https://pgc.up.edu.ph/temp/primerr')
primerr.name = 'ASFV-Primer R'
primerr.OT2SpecificProps = sbol3.TextProperty(primerr,'',0,1)
primerr.OT2SpecificProps = '{"coordinates":"D5", "source":"reservoir"}' 
doc.add(primerr)

probe = sbol3.Component('probe', 'https://pgc.up.edu.ph/temp/probe')
probe.name = 'ASFV-Probe'
probe.OT2SpecificProps = sbol3.TextProperty(probe,'',0,1)
probe.OT2SpecificProps = '{"coordinates":"A6", "source":"reservoir"}' 
doc.add(probe)

enzyme = sbol3.Component('enzyme', 'https://pgc.up.edu.ph/temp/agpath_enzyme')
enzyme.name = 'AgPath-ID™ One-Step RT-PCR, RT-PCR Enzyme Mix'
enzyme.OT2SpecificProps = sbol3.TextProperty(enzyme,'',0,1)
enzyme.OT2SpecificProps = '{"coordinates":"B6", "source":"reservoir"}' 
doc.add(enzyme)

buffer = sbol3.Component('buffer', 'https://pgc.up.edu.ph/temp/agpath_buffer')
buffer.name = 'AgPath-ID™ One-Step RT-PCR, RT-PCR Buffer '
buffer.OT2SpecificProps = sbol3.TextProperty(buffer,'',0,1)
buffer.OT2SpecificProps = '{"coordinates":"B5", "source":"reservoir"}' 
doc.add(buffer)



# actual steps of the protocol
# get a plate
platespec = paml.ContainerSpec(queryString="opentrons_96_aluminumblock_generic_pcr_strip_200ul", prefixMap=PREFIX_MAP, name='pcr')
platespec.OT2SpecificProps = sbol3.TextProperty(platespec1,"https://bioprotocols.org/paml/primitives/sample_arrays/EmptyContainer/OT2/Deck",0,1)
platespec.OT2SpecificProps = '{"deck":"6"}'
pcr = protocol.primitive_step('EmptyContainer', specification=platespec)

mixspec = paml.ContainerSpec(queryString="nest_96_wellplate_2ml_deep", prefixMap=PREFIX_MAP, name='mix')
mixspec.OT2SpecificProps = sbol3.TextProperty(platespec1,"https://bioprotocols.org/paml/primitives/sample_arrays/EmptyContainer/OT2/Deck",0,1)
mixspec.OT2SpecificProps = '{"deck":"10"}'
mix = protocol.primitive_step('EmptyContainer', specification=mixspec)

sample_count=96

mix_well1 = protocol.primitive_step('PlateCoordinates', source=mix.output_pin('samples'), coordinates="A1")
mix_well2 = protocol.primitive_step('PlateCoordinates', source=mix.output_pin('samples'), coordinates="A2")
provision_nfw1 = protocol.primitive_step('Provision', resource=nfw, destination=mix_well1.output_pin('samples'),amount=sbol3.Measure((3.75*(sample_count+2))/2, tyto.OM.microliter))
provision_primerf1 = protocol.primitive_step('Provision', resource=primerf, destination=mix_well1.output_pin('samples'),amount=sbol3.Measure((0.75*(sample_count+2))/2, tyto.OM.microliter))
provision_primerr1 = protocol.primitive_step('Provision', resource=primerr, destination=mix_well1.output_pin('samples'),amount=sbol3.Measure((0.75*(sample_count+2))/2, tyto.OM.microliter))
provision_probe1 = protocol.primitive_step('Provision', resource=probe, destination=mix_well1.output_pin('samples'),amount=sbol3.Measure((1.25*(sample_count+2))/2, tyto.OM.microliter))
provision_enzyme1 = protocol.primitive_step('Provision', resource=enzyme, destination=mix_well1.output_pin('samples'),amount=sbol3.Measure((1.00*(sample_count+2))/2, tyto.OM.microliter))
provision_buffer1 = protocol.primitive_step('Provision', resource=buffer, destination=mix_well1.output_pin('samples'),amount=sbol3.Measure((12.5*(sample_count+2))/2, tyto.OM.microliter),mixCycles=sbol3.Measure((5, tyto.OM.count)))

provision_nfw2 = protocol.primitive_step('Provision', resource=nfw, destination=mix_well2.output_pin('samples'),amount=sbol3.Measure((3.75*(sample_count+2))/2, tyto.OM.microliter))
provision_primerf2 = protocol.primitive_step('Provision', resource=primerf, destination=mix_well2.output_pin('samples'),amount=sbol3.Measure((0.75*(sample_count+2))/2, tyto.OM.microliter))
provision_primerr2 = protocol.primitive_step('Provision', resource=primerr, destination=mix_well2.output_pin('samples'),amount=sbol3.Measure((0.75*(sample_count+2))/2, tyto.OM.microliter))
provision_probe2 = protocol.primitive_step('Provision', resource=probe, destination=mix_well2.output_pin('samples'),amount=sbol3.Measure((1.25*(sample_count+2))/2, tyto.OM.microliter))
provision_enzyme2 = protocol.primitive_step('Provision', resource=enzyme, destination=mix_well2.output_pin('samples'),amount=sbol3.Measure((1.00*(sample_count+2))/2, tyto.OM.microliter))
provision_buffer2 = protocol.primitive_step('Provision', resource=buffer, destination=mix_well2.output_pin('samples'),amount=sbol3.Measure((12.5*(sample_count+2))/2, tyto.OM.microliter),mixCycles=sbol3.Measure((5, tyto.OM.count)))

transfer_dest1= protocol.primitive_step('PlateCoordinates', source=pcr.output_pin('samples'), coordinates="A1:H6")
transfer1 = protocol.primitive_step('TransferInto', source=mix_well1.output_pin('samples'), destination=transfer_dest1.output_pin('samples'), amount=sbol3.Measure(20, tyto.OM.microliter), mixCycles=sbol3.Measure(2,tyto.OM.count))

transfer_dest2= protocol.primitive_step('PlateCoordinates', source=pcr.output_pin('samples'), coordinates="A7:H12")
transfer2 = protocol.primitive_step('TransferInto', source=mix_well2.output_pin('samples'), destination=transfer_dest2.output_pin('samples'), amount=sbol3.Measure(20, tyto.OM.microliter), mixCycles=sbol3.Measure(2,tyto.OM.count))

leftTiprackSettingJSON = '{"pipette":"p1000_single_gen2","tipracks":[{"id":"geb_96_tiprack_1000ul","deck":11}]}'
rightTiprackSettingJSON = '{"pipette":"p300_single_gen2","tipracks":[{"id":"opentrons_96_tiprack_300ul","deck":4}]}'

filename=f'{protocol.name}.py'
agent = sbol3.Agent("auto_agent")
ee = ExecutionEngine(specializations=[OT2Specialization("2.11",leftTiprackSettingJSON,rightTiprackSettingJSON)])
parameter_values = []
execution = ee.execute(protocol, agent, id="execution")
with open(filename, 'w') as f:
     print(ee.specializations[0].script,file=f)
print(f"All done. Script dumped to {filename}.")

v = doc.validate()
assert len(v) == 0, "".join(f'\n {e}' for e in v)

temp_name = os.path.join(tempfile.gettempdir(), 'ludox.nt')
doc.write(temp_name, sbol3.SORTED_NTRIPLES)
print(f'Wrote file as {temp_name}')

 #render and view the dot
dot = protocol.to_dot()
dot.render(f'{protocol.name}.gv')
dot.view()
