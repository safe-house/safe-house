#ifndef __BLE_GAS_SERVICE_H__
#define __BLE_GAS_SERVICE_H__

class GasService {
public:
    const static uint16_t GAS_SERVICE_UUID              = 0xA000;
    const static uint16_t GAS_CO2_CHARACTERISTIC_UUID   = 0xA001;
    const static uint16_t GAS_TVOC_CHARACTERISTIC_UUID   = 0xA002;

    GasService(BLEDevice &_ble, uint16_t initialValue):
    ble(_ble), gasCO2(GAS_CO2_CHARACTERISTIC_UUID, &initialValue, GattCharacteristic::BLE_GATT_CHAR_PROPERTIES_NOTIFY),
    gasTVOC(GAS_TVOC_CHARACTERISTIC_UUID, &initialValue, GattCharacteristic::BLE_GATT_CHAR_PROPERTIES_NOTIFY)
    {
        GattCharacteristic *charTable[] = {&gasCO2, &gasTVOC};
        GattService         gasService(GAS_SERVICE_UUID, charTable, sizeof(charTable) / sizeof(GattCharacteristic *));

        ble.gattServer().addService(gasService);
    }

    GattAttribute::Handle_t getValueHandle() const
    {
        return gasCO2.getValueHandle();
    }

    void updateGasState(uint16_t ppmCO2, uint16_t ppmTVOC){
        uint8_t bytes[2];
        bytes[1] = ppmCO2 & 0xff;
        bytes[0] = (ppmCO2 >> 8);
        ble.gattServer().write(gasCO2.getValueHandle(), (uint8_t*)bytes, sizeof(bytes));
        bytes[1] = ppmTVOC & 0xff;
        bytes[0] = (ppmTVOC >> 8);
        ble.gattServer().write(gasTVOC.getValueHandle(), (uint8_t*)bytes, sizeof(bytes));
    }

private:
    BLEDevice                         &ble;
    ReadOnlyGattCharacteristic<uint16_t> gasCO2;
    ReadOnlyGattCharacteristic<uint16_t> gasTVOC;
};
#endif /* #ifndef __BLE_GAS_SERVICE_H__ */  