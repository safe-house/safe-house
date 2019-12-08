#include <events/mbed_events.h>
#include <mbed.h>
#include "ble/BLE.h"
#include "ble/DiscoveredCharacteristic.h"
#include "ble/DiscoveredService.h"
#include "ble/gap/Gap.h"
#include "ble/gap/AdvertisingDataParser.h"
#include "pretty_printer.h"

const static char PEER_NAME[] = "GAS";

static EventQueue event_queue(/* event count */ 10 * EVENTS_EVENT_SIZE);

static DiscoveredCharacteristic led_characteristic;
static int trigger_led_characteristic = 0;
uint16_t _discovered_UUID = 0x0000;
GattAttribute::Handle_t _CCCD_handle(0);

void lookForDeskriptors(void);

void onUpdatesCallback(const GattHVXCallbackParams *updates){
    printf("update received: handle %u\r\n", updates->handle);
    if (updates->handle == led_characteristic.getValueHandle()) {
        const uint8_t *p_data = updates->data;
        printf(
            "updates received: connHandle: %u, attrHandle: %u, Type: %x, Data: ",
            updates->connHandle,
            updates->handle,
            updates->type
        );
        for (unsigned index = 0; index < updates->len; index++) {
            printf("%02x ", updates->data[index]);
        }
        printf("\r\n");
    }
}

void characteristicDescriptorDiscoveryCallback(
    const CharacteristicDescriptorDiscovery::DiscoveryCallbackParams_t *charParams
) {
    printf("descriptor found with:\n");
    printf("connection_handle[%u] UUID[%X] attribute_Handle[%u]\r\n",
        charParams->descriptor.getConnectionHandle(),
        charParams->descriptor.getUUID().getShortUUID(),
        charParams->descriptor.getAttributeHandle()
    );

    // no reason to pursue the descriptor discovery at this point
    // request to terminate it then get notified in the termination callback
    if (charParams->descriptor.getUUID().getLen() != UUID::LENGTH_OF_LONG_UUID &&
        charParams->descriptor.getUUID().getShortUUID() == BLE_UUID_DESCRIPTOR_CLIENT_CHAR_CONFIG
    ) {
        _discovered_UUID = charParams->descriptor.getUUID().getShortUUID();
        _CCCD_handle = charParams->descriptor.getAttributeHandle();

        GattClient& client = BLE::Instance().gattClient();
        client.terminateCharacteristicDescriptorDiscovery(led_characteristic);
        printf("CCCD found; explicit termination of descriptors discovery\r\n");
    }
}

void write_cccd() {
    // cccd are 16 bit bit long; indication flag is on bit 2
    uint16_t cccd_value = BLE_HVX_NOTIFICATION;
    GattClient& client = BLE::Instance().gattClient();

    ble_error_t err = client.write(
        GattClient::GATT_OP_WRITE_REQ,
        led_characteristic.getConnectionHandle(),
        _CCCD_handle,
        sizeof(cccd_value),
        (uint8_t*) &cccd_value
    );

    if(err == 0){
        printf("cccd update sent successful\r\n");
        client.onHVX(onUpdatesCallback);
    }else{
        printf("error updating: error_code [%u]\n", err);
    }
}

void descriptorDiscoveryTerminationCallback(
    const CharacteristicDescriptorDiscovery::TerminationCallbackParams_t *termParams
) {
    if (termParams->error_code == 0 && _discovered_UUID == BLE_UUID_DESCRIPTOR_CLIENT_CHAR_CONFIG) {
        
        printf("descriptorDiscovery terminated without errors\r\n");
        printf("cccd with handle [%u] found!\r\n", _CCCD_handle);
        event_queue.call(write_cccd);
    }

    
    printf("UUID: %u\n", (unsigned int)_discovered_UUID);
    printf("\nno cccd found\r\n");
}

void service_discovery(const DiscoveredService *service) {
    if (service->getUUID().shortOrLong() == UUID::UUID_TYPE_SHORT) {
        printf("S UUID-%x attrs[%u %u]\r\n", service->getUUID().getShortUUID(), service->getStartHandle(), service->getEndHandle());
    } else {
        printf("S UUID-");
        const uint8_t *longUUIDBytes = service->getUUID().getBaseUUID();
        for (unsigned i = 0; i < UUID::LENGTH_OF_LONG_UUID; i++) {
            printf("%02x", longUUIDBytes[i]);
        }
        printf(" attrs[%u %u]\r\n", service->getStartHandle(), service->getEndHandle());
    }
}

void characteristic_discovery(const DiscoveredCharacteristic *characteristicP) {
    printf("  C UUID-%x valueAttr[%u] props[%x]\r\n", characteristicP->getUUID().getShortUUID(), characteristicP->getValueHandle(), (uint8_t)characteristicP->getProperties().broadcast());
    if (characteristicP->getUUID().getShortUUID() == 0xa001) { /* !ALERT! Alter this filter to suit your device. */
        led_characteristic        = *characteristicP;
        trigger_led_characteristic = true;
    }
}

void discovery_termination(Gap::Handle_t connectionHandle) {
    printf("terminated SD for handle %u\r\n", connectionHandle);
    if (trigger_led_characteristic) {
        trigger_led_characteristic = false;
        event_queue.call(lookForDeskriptors);
    }
}

void lookForDeskriptors(void) {
    printf("    \n");
    BLE &ble = BLE::Instance();

    printf(
        "start looking for Descriptors of characteristic %d, range [%d, %d] now\r\n",
        led_characteristic.getValueHandle(),
        led_characteristic.getValueHandle() + 1,
        led_characteristic.getLastHandle()
    );
    ble.gattClient().discoverCharacteristicDescriptors(
        led_characteristic,
        characteristicDescriptorDiscoveryCallback,
        descriptorDiscoveryTerminationCallback
    );
}


class LEDBlinkerDemo : ble::Gap::EventHandler {
public:
    LEDBlinkerDemo(BLE &ble, events::EventQueue &event_queue) :
        _ble(ble),
        _event_queue(event_queue),
        _alive_led(LED1, 1),
        _is_connecting(false) { }

    ~LEDBlinkerDemo() { }

    void start() {
        printf("Starting...");
        _ble.gap().setEventHandler(this);

        _ble.init(this, &LEDBlinkerDemo::on_init_complete);

        _event_queue.call_every(500, this, &LEDBlinkerDemo::blink);

        _event_queue.dispatch_forever();
    }

private:
    /** Callback triggered when the ble initialization process has finished */
    void on_init_complete(BLE::InitializationCompleteCallbackContext *params) {
        if (params->error != BLE_ERROR_NONE) {
            printf("Ble initialization failed.");
            return;
        }

        print_mac_address();

        ble::ScanParameters scan_params;
        _ble.gap().setScanParameters(scan_params);
        _ble.gap().startScan();
    }

    void blink() {
        _alive_led = !_alive_led;
    }

private:
    /* Event handler */

    void onDisconnectionComplete(const ble::DisconnectionCompleteEvent&) {
        _ble.gap().startScan();
        _is_connecting = false;
    }

    void onConnectionComplete(const ble::ConnectionCompleteEvent& event) {
        printf("Connected\n");
        if (event.getOwnRole() == ble::connection_role_t::CENTRAL) {
            _ble.gattClient().onServiceDiscoveryTermination(discovery_termination);
            _ble.gattClient().launchServiceDiscovery(
                event.getConnectionHandle(),
                service_discovery,
                characteristic_discovery,
                0xa000,
                0xa001
            );
        } else {
            _ble.gap().startScan();
        }
        _is_connecting = false;
    }

    void onAdvertisingReport(const ble::AdvertisingReportEvent &event) {
        /* don't bother with analysing scan result if we're already connecting */
        if (_is_connecting) {
            return;
        }
        printf("Scanned\n");

        ble::AdvertisingDataParser adv_data(event.getPayload());

        /* parse the advertising payload, looking for a discoverable device */
        while (adv_data.hasNext()) {
            ble::AdvertisingDataParser::element_t field = adv_data.next();

            printf("hi\n");
            if (field.type == ble::adv_data_type_t::COMPLETE_LOCAL_NAME){
                printf("True 1");
            }
            if (field.value.size() == strlen(PEER_NAME)){
                printf("True 2");
            }
            if ((memcmp(field.value.data(), PEER_NAME, field.value.size()) == 0)){
                printf("True 3");
            }
            /* connect to a discoverable device */
            if (field.type == ble::adv_data_type_t::COMPLETE_LOCAL_NAME &&
                field.value.size() == strlen(PEER_NAME) &&
                (memcmp(field.value.data(), PEER_NAME, field.value.size()) == 0)) {

                printf("Adv from: ");
                print_address(event.getPeerAddress().data());
                printf(" rssi: %d, scan response: %u, connectable: %u\r\n",
                       event.getRssi(), event.getType().scan_response(), event.getType().connectable());

                ble_error_t error = _ble.gap().stopScan();

                if (error) {
                    print_error(error, "Error caused by Gap::stopScan");
                    return;
                }

                const ble::ConnectionParameters connection_params;

                error = _ble.gap().connect(
                    event.getPeerAddressType(),
                    event.getPeerAddress(),
                    connection_params
                );

                if (error) {
                    _ble.gap().startScan();
                    return;
                }

                /* we may have already scan events waiting
                 * to be processed so we need to remember
                 * that we are already connecting and ignore them */
                _is_connecting = true;

                return;
            }
        }
    }

private:
    BLE &_ble;
    events::EventQueue &_event_queue;
    DigitalOut _alive_led;
    bool _is_connecting;
};

/** Schedule processing of events from the BLE middleware in the event queue. */
void schedule_ble_events(BLE::OnEventsToProcessCallbackContext *context) {
    event_queue.call(Callback<void()>(&context->ble, &BLE::processEvents));
}

int main()
{
    BLE &ble = BLE::Instance();
    ble.onEventsToProcess(schedule_ble_events);

    LEDBlinkerDemo demo(ble, event_queue);
    demo.start();

    return 0;
}