#include <events/mbed_events.h>
#include <mbed.h>
#include "ble/BLE.h"
#include "GasService.h"
#include "pretty_printer.h"


////////////////////////////////////////////////
#define CCS811_I2C_ADDR                 0xB4
#define CCS811_REG_STATUS               0x00    //Status.
#define CCS811_REG_MEAS_MODE            0x01    //Mesurement mode and conditions register.
#define CCS811_REG_ALG_RESULT_DATA      0x02    //Algorithm result. 2 bytes co2 ppm next 2 bytes ppb VOC level.
#define CCS811_REG_RAW_DATA             0x03    //Raw ADC data.
#define CCS811_REG_ENV_DATA             0x05    //Temperature and humidity data can be write to enavle compensation.
#define CCS811_REG_NTC                  0x06    //Provides the voltage across the reference registor and the voltage across the NTC resistor.
#define CCS811_REG_THRESHOLDS           0x10    //Thresholds for operation when interrupts are only generated when eCO2 ppm crosses a threshold.
#define CCS811_REG_BASELINE             0x11    //The encoded current baseline value can be read.A previously saved encoded baseline can be written.
#define CCS811_REG_HW_ID                0x20    //Hardware ID. The value is 0x81.
#define CCS811_REG_HW_VERSION           0x21    //Hardware version. The value is 0x1X.
#define CCS811_REG_BOOT_VERSION         0x23    //Firmware boot version. The First 2 bytes contain the firmware version number for the boot code.
#define CCS811_REG_APP_VERSION          0x24    //Firmware application version. The first 2 bytes contain the firmware version number for the application code.
#define CCS811_REG_ERROR_ID             0xE0    //Error ID. When the status register reports and error its source is lcated in this register.
#define CCS811_REG_APP_START            0xF4    //Application start. Used to transition the CCS811 state from boot to application mode, a write with no data is required. Before performing a write to APP_START the Status register should be accessed to check if there is a valid application present.
#define CCS811_REG_SW_RESET             0xFF    //If the correct 4 byres (0x11, 0xE5, 0x72, 0x8A)are written to this register in a single sequence the device will reset and return to BOOT bode.
 
//mode setting
#define CCS811_MEASUREMENT_MODE0        0x00    //Idle(Measurements are disabled in this mode).
#define CCS811_MEASUREMENT_MODE1        0x10    //Constant power mode, IAQ measurement every second.
#define CCS811_MEASUREMENT_MODE2        0x20    //Pulse heating mode IAQ measurement every 10 seconds.
#define CCS811_MEASUREMENT_MODE3        0x30    //Low power pulse heating mode IAQ measurement every 60 seconds.
#define CCS811_MEASUREMENT_MODE4        0x40    //Constant power mode, sensor measurement every 250ms. 1xx: Reserved modes (For future use).
 
//Interrupt control 
#define CCS811_INT_DATARDY              0x08    //At the end of each measurement cycle (250ms, 1s, 10s, 60s) a flag is set in the STATUS register regardless of the setting of this bit.
#define CCS811_INT_THRESH               0x04    //0: Interrupt mode (if enabled) operates normally 1: Interrupt mode (if enabled) only asserts the nINT signal (driven low) if the new ALG_RESULT_DATA crosses one of the thresholds set in the THRESHOLDS register by more than the hysteresis value (also in the THRESHOLDS register).
///////////////////////////////////////////////

const static char DEVICE_NAME[] = "GAS";

static EventQueue event_queue(/* event count */ 10 * EVENTS_EVENT_SIZE);

I2C i2c(p26, p27);

class LEDDemo : ble::Gap::EventHandler {
public:
    LEDDemo(BLE &ble, events::EventQueue &event_queue) :
        _ble(ble),
        _event_queue(event_queue),
        _alive_led(P0_17, 1),
        _actuated_led(LED2, 0),
        _gas_uuid(GasService::GAS_SERVICE_UUID),
        _gas_service(NULL),
        _adv_data_builder(_adv_buffer) { }

    ~LEDDemo() {
        delete _gas_service;
    }

    void start() {
        _ble.gap().setEventHandler(this);

        _ble.init(this, &LEDDemo::on_init_complete);

        _event_queue.call_every(2000, this, &LEDDemo::blink);

        _event_queue.dispatch_forever();
    }

private:
    /** Callback triggered when the ble initialization process has finished */
    void on_init_complete(BLE::InitializationCompleteCallbackContext *params) {
        if (params->error != BLE_ERROR_NONE) {
            printf("Ble initialization failed.");
            return;
        }

        _gas_service = new GasService(_ble, 1);

        _ble.gattServer().onDataWritten(this, &LEDDemo::on_data_written);

        print_mac_address();

        start_advertising();
    }

    void start_advertising() {
        /* Create advertising parameters and payload */

        ble::AdvertisingParameters adv_parameters(
            ble::advertising_type_t::CONNECTABLE_UNDIRECTED,
            ble::adv_interval_t(ble::millisecond_t(1000))
        );

        _adv_data_builder.setFlags();
        _adv_data_builder.setLocalServiceList(mbed::make_Span(&_gas_uuid, 1));
        _adv_data_builder.setName(DEVICE_NAME);

        /* Setup advertising */

        ble_error_t error = _ble.gap().setAdvertisingParameters(
            ble::LEGACY_ADVERTISING_HANDLE,
            adv_parameters
        );

        if (error) {
            printf("_ble.gap().setAdvertisingParameters() failed\r\n");
            return;
        }

        error = _ble.gap().setAdvertisingPayload(
            ble::LEGACY_ADVERTISING_HANDLE,
            _adv_data_builder.getAdvertisingData()
        );

        if (error) {
            printf("_ble.gap().setAdvertisingPayload() failed\r\n");
            return;
        }

        /* Start advertising */

        error = _ble.gap().startAdvertising(ble::LEGACY_ADVERTISING_HANDLE);

        if (error) {
            printf("_ble.gap().startAdvertising() failed\r\n");
            return;
        }
    }

    /**
     * This callback allows the LEDService to receive updates to the ledState Characteristic.
     *
     * @param[in] params Information about the characterisitc being updated.
     */
    void on_data_written(const GattWriteCallbackParams *params) {
        if ((params->handle == _gas_service->getValueHandle()) && (params->len >= 1)) {
            _actuated_led = 1;
        }
    }

    void blink() {
        _alive_led = !_alive_led;
        getCO2();
        _gas_service->updateGasState(_eCO2, _TVOC);
    }

    void getCO2(){
        char recv[8];
        char send[1];
    
        send[0] = CCS811_REG_ALG_RESULT_DATA;
        i2c.write(CCS811_I2C_ADDR, send, 1, true);
        i2c.read(CCS811_I2C_ADDR, recv, 8, false);

		_eCO2 = ((uint16_t)recv[0] << 8) | ((uint16_t)recv[1]);
		_TVOC = ((uint16_t)recv[2] << 8) | ((uint16_t)recv[3]);

        printf("CO2: %u\n", (unsigned int)_eCO2);
        printf("TVOC: %u\n", (unsigned int)_TVOC);

    }


private:
    /* Event handler */

    void onDisconnectionComplete(const ble::DisconnectionCompleteEvent&) {
        _ble.gap().startAdvertising(ble::LEGACY_ADVERTISING_HANDLE);
    }

private:
    BLE &_ble;
    events::EventQueue &_event_queue;
    DigitalOut _alive_led;
    DigitalOut _actuated_led;

    uint16_t _eCO2;
    uint16_t _TVOC;

    UUID _gas_uuid;
    GasService *_gas_service;

    uint8_t _adv_buffer[ble::LEGACY_ADVERTISING_MAX_SIZE];
    ble::AdvertisingDataBuilder _adv_data_builder;
};

/** Schedule processing of events from the BLE middleware in the event queue. */
void schedule_ble_events(BLE::OnEventsToProcessCallbackContext *context) {
    event_queue.call(Callback<void()>(&context->ble, &BLE::processEvents));
}

int main()
{

    // BLE &ble = BLE::Instance();
    // ble.onEventsToProcess(schedule_ble_events);
    // LEDDemo demo(ble, event_queue);
    // demo.start();


    char send[2];
    char read[8];
    char hwv[8];
    char hwd[8];
    
    // Write app start
    send[0] = CCS811_REG_APP_START; //0xF4
    i2c.write(CCS811_I2C_ADDR, send, 1);

    
    // Write measurement mode    
    send[0] = CCS811_REG_MEAS_MODE; //0x01
    send[1] = CCS811_MEASUREMENT_MODE1; //0x10
    i2c.write(CCS811_I2C_ADDR, send, 2);

    printf("inited");

    //wait for availability
    while ((hwd[0] >> 3) & 0x01 != 1){
        read[0] = CCS811_REG_STATUS; //0x00
    
        wait_us(50000);
    
        i2c.write(CCS811_I2C_ADDR, read, 1);
        i2c.read(CCS811_I2C_ADDR, hwd, 1);
        printf("STATUS 0x%X\r\n", hwd[0]);
    }

    BLE &ble = BLE::Instance();
    ble.onEventsToProcess(schedule_ble_events);

    LEDDemo demo(ble, event_queue);
    demo.start();

    return 0;
}
