#
#  GoogleFindMyTools - A set of tools to interact with the Google Find My API
#  Copyright © 2024 Leon Böttger. All rights reserved.
#

from ProtoDecoders import DeviceUpdate_pb2

class WrappedLocation:
    def __init__(self, decrypted_location, time, accuracy, status, is_own_report, name):
        self.time = time
        self.status = status
        self.decrypted_location = decrypted_location
        self.is_own_report = is_own_report
        self.accuracy = accuracy
        self.name = name

        if (self.decrypted_location):
            self._proto_loc = DeviceUpdate_pb2.Location()
            self._proto_loc.ParseFromString(self.decrypted_location)

    @property
    def latitude(self):
        if (self._proto_loc):
            return self._proto_loc.latitude / 1e7
        return None

    @property
    def longitude(self):
        if (self._proto_loc):
            return self._proto_loc.longitude / 1e7
        return None

    @property
    def altitude(self):
        if (self._proto_loc):
            return self._proto_loc.altitude
        return None
