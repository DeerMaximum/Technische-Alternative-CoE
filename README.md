# Home Assistant integration to read Values from C.M.I
[![GitHub Release][releases-shield]][releases]
[![hacs][hacsbadge]][hacs]

The integration polls the digital and analog data from a [Technische Alternative][taWebsite] C.M.I. via the CanOverEthernet(CoE) interface.

The data is fetched every minute.

To apply changes from the CoE configuration, reload the integration.

> **Note**
> This integration requires the [Coe to HTTP add-on][CoEHttpAddon].

> When using CoE V2, scaling errors may occur as a new system is used to scale the values.
> In the case of such an error, please create a ticket.

{% if not installed %}
## Installation

### Step 1:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=DeerMaximum&repository=Technische-Alternative-CoE&category=integration)

### Step 2 (**Don't forget**):

1. Click install.
2. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Technische Alternative".

{% endif %}

## Configuration

The integration automatically detects if the [Coe to HTTP add-on][CoEHttpAddon] is installed in the Home Assistant instance, in which case only providing a target CAN-ID is necessary. 
To configure CoE on your C.M.I., follow [these](https://wiki.fhem.de/wiki/CanOverEthernet) instructions (German). The CAN-ID that you must provide is the same one configured under point six in the *Konfigurieren des CMI* section.
 

If an external server is used, the IP and PORT of this server must be specified during setup.

### Receive values

New channels are automatically recognized when the integration is reloaded.

### Send values
You can configure the entities to be sent to the C.M.I. after the initial setup. 
The values are transmitted on change and every 10 minutes.

The following domains are supported:
* sensor
* binary_sensor
* number
* input_number
* input_boolean

[taWebsite]: https://www.ta.co.at/
[CoEHttpAddon]: https://github.com/DeerMaximum/ha-addons/tree/main/ta_coe
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/v/release/DeerMaximum/Technische-Alternative-CoE.svg?style=for-the-badge
[releases]: https://github.com/DeerMaximum/Technische-Alternative-CoE/releases
