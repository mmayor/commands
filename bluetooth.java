package com.darklab.ble;


import android.app.Activity;
import android.bluetooth.BluetoothGattDescriptor;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.util.Base64;
import android.util.Log;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import  android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Button;

public class Bluetooth {

    private Context context;
    public BluetoothAdapter bluetoothAdapter;
    private BluetoothLeScanner scanner;
    private ScanSettings settings;
    public BluetoothGatt gatt;
    public String stateNow = "STATE_OTHER";
    private BluetoothGattCallback gcallBack;
    public UUID hoberPower= UUID.fromString("3e3d4853-8116-23a9-e911-ac6230454a5f");
    public UUID hoberPowerService= UUID.fromString("3e3d4850-8116-23a9-e911-ac6230454a5f");
    // CHARACTERISTIC_COUNTER_UUID = UUID.fromString("31517c58-66bf-470c-b662-e352a6c80cba");
    // private EditText et1;

    public Bluetooth(Context context){
        this.context = context;
        final BluetoothManager bluetoothManager = (BluetoothManager) context.getSystemService(Context.BLUETOOTH_SERVICE);
        bluetoothAdapter = bluetoothManager.getAdapter();

    }

    public Boolean Update(String state){

        TextView textView= (TextView) ((Activity)context).findViewById(R.id.textView);
        textView.setText(state);
        Button button= (Button) ((Activity)context).findViewById(R.id.button);

        if (state== "STATE_CONNECTED") {
            button.setText("DISCONNECT");
            return true;
        } else {

                button.setText("CONNECT");
                return false;
        }
        }


    public void onResume(String name){

        Log.i("bluetooth", "Resume");
        scanner = bluetoothAdapter.getBluetoothLeScanner();
        settings = new ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).build();
        List<ScanFilter> filters = new ArrayList<ScanFilter>();
        ScanFilter scanFilter = new ScanFilter.Builder().setDeviceName(name).build();
        filters.add(scanFilter);
        scanner.startScan(filters, settings, callBack);
        Log.i("bluetooth", scanner.toString());
        Log.i("bluetooth", "state " + bluetoothAdapter.getScanMode());
    }

    private ScanCallback callBack = new ScanCallback(){
        @Override
        public void onScanResult(int callbackType, ScanResult result) {
            super.onScanResult(callbackType, result);
            Log.i("bluetooth", "Scan Result");
            Log.i("bluetooth", String.valueOf(callbackType));
            Log.i("bluetooth", result.toString());
            BluetoothDevice btDevice = result.getDevice();
            connectToDevice(btDevice);
        }
        @Override
        public void onBatchScanResults(List<ScanResult> results) {
            super.onBatchScanResults(results);
            for (ScanResult sr : results) {
                Log.i("bluetooth", sr.toString());
            }
        }
        @Override
        public void onScanFailed(int errorCode) {
            super.onScanFailed(errorCode);
            Log.i("bluetooth", "Error Code: " + errorCode);
        }
    };


    public void connectToDevice(BluetoothDevice device) {
        if (gatt == null) {
            gatt = device.connectGatt(this.context, false, gattCallback);


        }
    }


    private final BluetoothGattCallback gattCallback = new BluetoothGattCallback() {
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
            Log.i("bluetooth", "Status: " + status);
            switch (newState) {
                case BluetoothProfile.STATE_CONNECTED:
                    Log.i("bluetooth", "STATE_CONNECTED");
                    gatt.discoverServices();
                    stateNow= "STATE_CONNECTED";
                    Update(stateNow);
                    stopScanning();
                    break;
                case BluetoothProfile.STATE_DISCONNECTED:
                    Log.e("bluetooth", "STATE_DISCONNECTED");
                    stateNow= "STATE_DISCONNECTED";
                    Update(stateNow);
                    break;
                default:
                    Log.e("bluetooth", "STATE_OTHER");
                    stateNow= "STATE_OTHER";
                    Update(stateNow);
            }
        }
        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
            List<BluetoothGattService> services = gatt.getServices();
            Log.i("bluetooth", services.toString());
            for (BluetoothGattService service : services){
                Log.i("bluetooth", service.toString());
                List<BluetoothGattCharacteristic> charactheristics = service.getCharacteristics();
                Log.i("bluetooth", charactheristics.toString());

                for (BluetoothGattCharacteristic charactheristic : charactheristics){
                    gatt.readCharacteristic(charactheristic);


                    if (charactheristic.getUuid().equals(hoberPower)){

                        Log.i("CARACTERISTICA_FOUND", charactheristic.getUuid().toString());
                        byte[] value = new byte[1];
                        value[0] = (byte) (0x1);
                        charactheristic.setValue(value);
                       // boolean status = BluetoothGatt.writeCharacteristic(charac);

                        int format = -1;
                        format = BluetoothGattCharacteristic.FORMAT_UINT8;
                        if (charactheristic.getValue()==null){Log.i("PEPE", "PEPE");};
                        int flag = charactheristic.getProperties();

                        if ((flag & 0x01) != 0) {
                            format = BluetoothGattCharacteristic.FORMAT_UINT16;
                            Log.i("FORMAT_16", "Heart rate format UINT16.");
                        } else {
                            format = BluetoothGattCharacteristic.FORMAT_UINT8;
                            Log.i("FORMAT_8", "Heart rate format UINT8.");
                        }
                        //final int heartRate = charactheristic.getIntValue(format, 1);
                        // Log.i("RECEIVE_RATE", String.format("Received heart rate: %d", heartRate));
                        // intent.putExtra(EXTRA_DATA, String.valueOf(heartRate));

                    }


                    Log.i("CARACTERISTICA", charactheristic.getUuid().toString());
                    // Log.d("CharacteristicRead", String.valueOf(charactheristic)); // try to get characteristic uuid?
                    // Log.d("BLE_VALUE_READ", String.valueOf(charactheristic.getValue())); // Try to read value

                    /**
                    if (charactheristic.getValue() != null){
                        final byte[] data = charactheristic.getValue();
                        String finger_buffer = Base64.encodeToString(data, Base64.DEFAULT);
                        Log.i("Capturedbiometricdevice",   finger_buffer);
                    }
                    */



                    //  Log.i("CARACTERISTICA_VALUE", charactheristic.getValue().toString());
                }
            }

            writeCharacteristic(gatt, hoberPowerService, hoberPower);
        }



        @Override
        public void onCharacteristicRead(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
            Log.i("bluetooth", characteristic.toString());
            //gatt.disconnect();
        }


    };

    // @Override
    public boolean writeCharacteristic(BluetoothGatt gatt, UUID service, UUID  characteristic){

        //check mBluetoothGatt is available
        if (gatt == null) {
            Log.i("TAG_CONEXION", "lost connection");
            return false;
        }
        BluetoothGattService Service = gatt.getService(service);
        if (Service == null) {
            Log.i("TAG_SERVICE", "service not found!");
            return false;
        }
        BluetoothGattCharacteristic charac = Service
                .getCharacteristic(characteristic);
        if (charac == null) {
            Log.i("TAG_CHAR", "char not found!");
            return false;
        }

        byte[] value = new byte[1];
        value[0] = (byte) (0x01);
        charac.setValue(value);
        boolean status = gatt.writeCharacteristic(charac);
        return status;
    }



    public void stopScanning(){

        if (gatt == null) {
            return;
        }
        //canCallback gCallback = null;
        //scanner.stopScan(gCallback, callBack);
        scanner.stopScan(callBack);

    }

    
    public void onClose() {

        if (gatt == null) {
            return;
        }
        //canCallback gCallback = null;
        //scanner.stopScan(gCallback, callBack);
        scanner.stopScan(callBack);

        gatt.close();
        gatt = null;
        stateNow = "STATE_OTHER";
        Update(stateNow);


    }

    public void writeCharacteristicNew() {



    }
};

