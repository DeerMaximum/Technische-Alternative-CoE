"""CoE state sender to send values."""
from ta_cmi.const import UNITS_EN


class StateSender:
    """Handle the transfer to the CoE server."""

    @staticmethod
    def _map_unit_to_id(unit: str) -> str:
        """Map a str unit to C.M.I. ID."""
        ids = [k for k, v in UNITS_EN.items() if v == unit]

        if len(ids) == 0:
            return "0"

        return ids[-1]

    def update_digital_manuel(self, entity_id: str, state: bool):
        """"""

    async def update_digital(self, entity_id: str, state: bool):
        """"""

    def update_analog_manuel(self, entity_id: str, state: float, unit: str):
        """"""

    async def update_analog(self, entity_id: str, state: float, unit: str):
        """"""

    async def update(self):
        """"""
