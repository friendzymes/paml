#Protocol Name:iGEM 2018 LUDOX OD calibration protocol


from opentrons import protocol_api

metadata = {'apiLevel': '2.11'\}

leftTiprack0 = protocol.load_labware('geb_96_tiprack_1000ul', 4)
leftTiprack1 = protocol.load_labware('geb_96_tiprack_1000ul', 5)
left = protocol.load_instrument('p1000_single_gen2', 'left', tip_rack=leftTiprack0,leftTiprack1)
rightTiprack0 = protocol.load_labware('opentrons_96_tiprack_20ul', 6)
rightTiprack1 = protocol.load_labware('opentrons_96_tiprack_20ul', 7)
right = protocol.load_instrument('p20_single_gen2', 'right', tip_rack=rightTiprack0,rightTiprack1)


#Protocol Materials
#[ddH2O](https://identifiers.org/pubchem.substance:24901740)
reservoir = protocol.load_labware('nest_12_reservoir_15ml', 1)
#[LUDOX](https://identifiers.org/pubchem.substance:24866361)

#Steps
plate1 = protocol.load_labware('corning_48_wellplate_1.6ml_flat', 2)
plate2 = protocol.load_labware('corning_48_wellplate_1.6ml_flat', 3)
left.transfer(80.0,reservoir['A1'],plate1['A1:D1'])
right.transfer(90.0,reservoir['A2'],plate1['A2:D2'])
left.transfer(100.0,reservoir['A1'],plate2['A1:D1'])
right.transfer(110.0,reservoir['A2'],plate2['A2:D2'])

