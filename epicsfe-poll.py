#!/usr/bin/env python3

import time
import midas
import midas.frontend
import collections
from CaChannel import ca, CaChannel, CaChannelException

class EpicsEquipment(midas.frontend.EquipmentBase):

    def __init__(self, midas_client):
        default_common = midas.frontend.InitialEquipmentCommon()
        default_common.equip_type = midas.EQ_PERIODIC
        default_common.read_when = midas.RO_ALWAYS
        default_common.event_id = 60
        default_common.period_ms = 10000
        default_common.log_history = 1

        default_settings = collections.OrderedDict([ ("PV list", [''] * 50), ])

        midas.frontend.EquipmentBase.__init__(self, midas_client, "EpicsFrontend", default_common, default_settings)

    def readout_func(self):
        for pvName in self.settings['PV list']:
            if pvName == '': 
                continue
            try:
                chan = CaChannel()
                chan.searchw(pvName)
                pvValue = chan.getw()
                pvValue = round(pvValue, 2)
                chan.pend_io()
                #print(f"PV: {pvName} value: {pvValue}")
                self.client.odb_set(f'{self.odb_variables_dir}/{pvName}', pvValue)
            except CaChannelException as e:
                print(f'E: {pvName} {e}')

class EpicsFrontend(midas.frontend.FrontendBase):
    def __init__(self):
        midas.frontend.FrontendBase.__init__(self, "EpicsFrontend")

        self.add_equipment(EpicsEquipment(self.client))

if __name__ == "__main__":
    fe = EpicsFrontend()
    fe.run()

