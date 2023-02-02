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

      caChannels = []
      self.lastWritten = {}

      for pv in self.settings['PV list']:
         if pv == '': 
             continue
         try:
             chan = CaChannel()
             chan.searchw(pv)
             chan.add_masked_array_event(ca.DBR_STS_DOUBLE, None, None, self.eventCB, pv)
             chan.flush_io()
         except CaChannelException as e:
             print(f'E: {pv} {e}')
         else:
             caChannels.append(chan)

   def readout_func(self):
      None

   def eventCB(self, epics_args, user_args):
      pvName = user_args[0]
      pvValue = epics_args['pv_value']
      pvValue = round(pvValue, 2)

      if self.lastWritten.get('pvName', None) != None:
         if (time.time() - self.lastWritten['pvName']) > 10:		# check if time elapsed from last update > 10 seconds
            self.client.odb_set(f'{self.odb_variables_dir}/{pvName}', pvValue)

      self.lastWritten['pvName'] = time.time()

class EpicsFrontend(midas.frontend.FrontendBase):
   def __init__(self):
      midas.frontend.FrontendBase.__init__(self, "EpicsFrontend")

      self.add_equipment(EpicsEquipment(self.client))

if __name__ == "__main__":
   fe = EpicsFrontend()
   fe.run()

