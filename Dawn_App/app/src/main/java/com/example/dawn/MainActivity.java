package com.example.dawn;

import android.annotation.SuppressLint;
import android.app.AlertDialog;
import android.app.TimePickerDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.Build;
import android.os.StrictMode;

import androidx.annotation.ColorInt;
import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import androidx.appcompat.widget.SwitchCompat;
import androidx.appcompat.widget.Toolbar;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.ImageView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.TimePicker;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.concurrent.TimeUnit;

@SuppressLint("DefaultLocale")
@RequiresApi(api = Build.VERSION_CODES.JELLY_BEAN)
public class MainActivity extends AppCompatActivity {

    public static final String COLOUR = "colour";
    public static final String NEW_COLOUR = "new_colour";
    TimePickerDialog timePickerDialog;
    SeekBar brightnessSeekbar;
    SeekBar volumeSeekbar;

    Boolean stereo_on;
    Boolean bs_on;
    Boolean ls_on;
    Boolean sc_on;
    Short radio_volume;
    Short radio_station = 0;
    Boolean bl_on;
    Boolean ll_on;
    Boolean ol_on;
    Boolean kl_on;
    Boolean party_mode;

    Boolean new_colour;
    String newColourString;

    Integer red_pigment;
    Integer green_pigment;
    Integer blue_pigment;
    @ColorInt
    Integer colour;

    Boolean weekday_alarm_on;
    Short weekday_alarm_hours;
    Short weekday_alarm_minutes;
    Boolean weekend_alarm_on;
    Short weekend_alarm_hours;
    Short weekend_alarm_minutes;
    Short brightness_val;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitNetwork().build();
        StrictMode.setThreadPolicy(policy);
        setContentView(R.layout.activity_main);

        Intent intent = getIntent();
        if (intent != null && intent.getExtras() != null && intent.getExtras().containsKey(NEW_COLOUR)){
            new_colour = true;
            colour = intent.getIntExtra(NEW_COLOUR, getColor(R.color.warm_glow));
            red_pigment = Color.red(colour);
            green_pigment = Color.green(colour);
            blue_pigment = Color.blue(colour);

            String red_pigment_string = ("00" + Integer.toHexString(red_pigment)).substring(Integer.toHexString(red_pigment).length());
            String green_pigment_string = ("00" + Integer.toHexString(green_pigment)).substring(Integer.toHexString(green_pigment).length());
            String blue_pigment_string = ("00" + Integer.toHexString(blue_pigment)).substring(Integer.toHexString(blue_pigment).length());
            newColourString = "COLOUR#" + red_pigment_string + green_pigment_string + blue_pigment_string;
        }
        else {
            new_colour = false;
        }

        Toolbar myToolbar = (Toolbar) findViewById(R.id.my_toolbar);
        setSupportActionBar(myToolbar);
        brightnessSeekbar = findViewById(R.id.brightness);

        brightnessSeekbar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                if (b) {setBrightness (i);};
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        volumeSeekbar = findViewById(R.id.volume);

        volumeSeekbar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                if (b) {setVolume (i);};
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.standby, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (R.id.Off == item.getItemId()){
            sendMessage("kill");
            setSwitches();
        }
        return true;
    }

    @Override
    protected void onResume () {
        super.onResume();
        ConnectivityManager connManager = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo mWifi = connManager.getNetworkInfo(ConnectivityManager.TYPE_WIFI);
        if (mWifi.isConnected()) {
            try {
                Socket socket = new Socket("192.168.1.214", 12345);
                PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
                byte[] response = new byte[21];
                InputStream in = socket.getInputStream();
                if (new_colour) {
                    out.println(newColourString);
                    new_colour = false;
                }
                else {
                    out.println("Request");
                }
                in.read(response, 0, 21);
                processResponse(response);

            } catch (IOException ignored) {
                // Can't connect so close app
                Intent intent = new Intent(Intent.ACTION_MAIN);
                intent.addCategory(Intent.CATEGORY_HOME);
                startActivity(intent);
            }
        }
        else {
            // Not even connected to wifi so close app
            Intent intent = new Intent(Intent.ACTION_MAIN);
            intent.addCategory(Intent.CATEGORY_HOME);
            startActivity(intent);
        }
        setSwitches();
    }

    private void processResponse (byte [] response) throws UnsupportedEncodingException {
        stereo_on = Byte.toUnsignedInt(response[0]) == 1;
        bs_on = Byte.toUnsignedInt(response[1]) == 1;
        ls_on = Byte.toUnsignedInt(response[2]) == 1;
        sc_on = Byte.toUnsignedInt(response[3]) == 1;
        radio_volume = (short) Byte.toUnsignedInt(response[4]);
        radio_station = (short) Byte.toUnsignedInt(response[5]);
        bl_on = Byte.toUnsignedInt(response[6]) == 1;
        ll_on = Byte.toUnsignedInt(response[7]) == 1;
        ol_on = Byte.toUnsignedInt(response[8]) == 1;
        kl_on = Byte.toUnsignedInt(response[9]) == 1;
        party_mode = Byte.toUnsignedInt(response[10]) == 1;
        brightness_val = (short) Byte.toUnsignedInt(response[11]);
        red_pigment = Byte.toUnsignedInt(response[12]);
        green_pigment = Byte.toUnsignedInt(response[13]);
        blue_pigment = Byte.toUnsignedInt(response[14]);
        weekday_alarm_on = Byte.toUnsignedInt(response[15]) == 1;
        weekday_alarm_hours = (short) Byte.toUnsignedInt(response[16]);
        weekday_alarm_minutes = (short) Byte.toUnsignedInt(response[17]);
        weekend_alarm_on = Byte.toUnsignedInt(response[18]) == 1;
        weekend_alarm_hours = (short) Byte.toUnsignedInt(response[19]);
        weekend_alarm_minutes = (short) Byte.toUnsignedInt(response[20]);
    }

    @RequiresApi(api = Build.VERSION_CODES.JELLY_BEAN)
    private void setSwitches () {
        SwitchCompat stereo_switch = findViewById(R.id.stereo_switch);
        stereo_switch.setChecked(stereo_on);

        SwitchCompat bs = findViewById(R.id.brsound);
        bs.setChecked(bs_on);

        SwitchCompat ls = findViewById(R.id.lrsound);
        ls.setChecked(ls_on);

        SwitchCompat spotify = findViewById(R.id.spotify);
        spotify.setChecked(sc_on);

        SwitchCompat bl = findViewById(R.id.brl);
        bl.setChecked(bl_on);

        SwitchCompat ll = findViewById(R.id.lrl);
        ll.setChecked(ll_on);

        SwitchCompat ol = findViewById(R.id.ol);
        ol.setChecked(ol_on);

        SwitchCompat kl = findViewById(R.id.kl);
        kl.setChecked(kl_on);

        SwitchCompat pm = findViewById(R.id.pm);
        pm.setChecked(party_mode);

        ImageView[] stations = {
                findViewById(R.id.fip),
                findViewById(R.id.fip_electro),
                findViewById(R.id.triplej),
                findViewById(R.id.folk_forward),
                findViewById(R.id.gaydio),
                findViewById(R.id.bbc6)
        };

        SeekBar brightness = findViewById(R.id.brightness);
        brightness.setMax(63);
        brightness.setProgress(brightness_val);

        SeekBar volume = findViewById(R.id.volume);
        volume.setMax(6);
        volume.setProgress(radio_volume);

        for (int i = 0; i < stations.length; i++) {
            if (radio_station == i + 1) {
                stations[i].setBackground(getResources().getDrawable(R.drawable.border));
            }
            else {
                stations[i].setBackground(null);
            }
        }
        if (weekday_alarm_on) {
            findViewById(R.id.ClearMF).setVisibility(View.VISIBLE);
            TextView mfTime = findViewById(R.id.MF_Time);
            mfTime.setVisibility(View.VISIBLE);
            String minutesString = String.format("%02d", weekday_alarm_minutes);
            String alarmTime = weekday_alarm_hours + ":" + minutesString;
            mfTime.setText(alarmTime);
        }
        else {
            findViewById(R.id.ClearMF).setVisibility(View.INVISIBLE);
            findViewById(R.id.MF_Time).setVisibility(View.INVISIBLE);
        }
        if (weekend_alarm_on) {
            findViewById(R.id.ClearSS).setVisibility(View.VISIBLE);
            TextView ssTime = findViewById(R.id.SS_Time);
            ssTime.setVisibility(View.VISIBLE);
            String minutesString = String.format("%02d", weekend_alarm_minutes);
            String alarmTime = weekend_alarm_hours + ":" + minutesString;
            ssTime.setText(alarmTime);
        }
        else {
            findViewById(R.id.ClearSS).setVisibility(View.INVISIBLE);
            findViewById(R.id.SS_Time).setVisibility(View.INVISIBLE);
        }
    }

    private boolean sendMessage(String s){
        try {
            Socket socket = new Socket("192.168.1.214", 12345);
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            byte[] response = new byte[21];
            InputStream in = socket.getInputStream();
            out.println(s);
            in.read(response, 0, 21);
            processResponse(response);
            return true;
        }
        catch (IOException ignored){
            Context toastContext = getApplicationContext();
            CharSequence failure = "Unable to connect";
            int toastDuration = Toast.LENGTH_SHORT;
            Toast connectionFailedToast = Toast.makeText(toastContext, failure, toastDuration);
            connectionFailedToast.show();
            return false;
        }
    }

    public void switchStereo(View view){
        sendMessage("stereo");
        setSwitches();
    }

    public void toggleLivingRoom(View view) {
        sendMessage("living_room_speakers");
        setSwitches();
    }

    public void toggleBedRoom(View view) {
        sendMessage("bedroom_speakers");
        setSwitches();
    }

    public void toggleSpotify(View view) {
        sendMessage("spotify");
        setSwitches();
    }

    public void triplej (View view) {
        sendMessage("triplej");
        setSwitches();
    }

    public void gaydio (View view) {
        sendMessage("gaydio");
        setSwitches();
    }

    public void bbc6 (View view) {
        sendMessage("bbc6");
        setSwitches();
    }

    public void fip_electro (View view) {
        sendMessage("fip_electro");
        setSwitches();
    }

    public void fip (View view) {
        sendMessage("fip");
        setSwitches();
    }

    public void folk_forward (View view) {
        sendMessage("folk_forward");
        setSwitches();
    }

    public void bedroomLights(View view) {
        sendMessage("bedroom_lights");
        setSwitches();
    }

    public void livingRoomLights(View view) {
        sendMessage("living_room_lights");
        setSwitches();
    }

    public void officeLights(View view) {
        sendMessage("office_lights");
        setSwitches();
    }

    public void kitchenLights(View view) {
        sendMessage("kitchen_lights");
        setSwitches();
    }

    public void partyMode(View view) throws InterruptedException {
        sendMessage("party_mode");
        TimeUnit.MILLISECONDS.sleep(10);
        sendMessage("Request");
        setSwitches();
    }

    public void colourPicker(View view) {
        colour = Color.rgb(red_pigment, green_pigment, blue_pigment);
        Intent intent = new Intent(this, ColourPicker.class);
        intent.putExtra(COLOUR, colour);
        startActivity(intent);
    }

    public void setMFAlarm(View view) {
        timePickerDialog = new TimePickerDialog(MainActivity.this, new TimePickerDialog.OnTimeSetListener() {
            @Override
            public void onTimeSet(TimePicker timePicker, int hourOfDay, int minutes) {
                String alarmText = "ALARM#MF#" + hourOfDay + ":" + minutes;
                if (sendMessage(alarmText)){
                    setSwitches();
                    Context toastContext = getApplicationContext();
                    int toastDuration = Toast.LENGTH_SHORT;
                    String minutesString = String.format("%02d", minutes).replace(" ", "0");
                    String toastText = ("Alarm set for " + hourOfDay + ":" + minutesString);
                    Toast alarmSuccessToast = Toast.makeText(toastContext, toastText, toastDuration);
                    alarmSuccessToast.show();
                }
            }
        }, 7, 0, true);
        timePickerDialog.show();
    }

    public void clearMFAlarm(View view) {
        if (sendMessage("CLEAR#MF")){
            setSwitches();
            Context toastContext = getApplicationContext();
            int toastDuration = Toast.LENGTH_SHORT;
            String toastText = ("Weekday Alarm cancelled");
            Toast alarmCancelToast = Toast.makeText(toastContext, toastText, toastDuration);
            alarmCancelToast.show();
        }
    }

    public void setSSAlarm(View view) {
        timePickerDialog = new TimePickerDialog(MainActivity.this, new TimePickerDialog.OnTimeSetListener() {
            @Override
            public void onTimeSet(TimePicker timePicker, int hourOfDay, int minutes) {
                String alarmText = "ALARM#SS#" + hourOfDay + ":" + minutes;
                if (sendMessage(alarmText)){
                    setSwitches();
                    Context toastContext = getApplicationContext();
                    int toastDuration = Toast.LENGTH_SHORT;
                    String minutesString = String.format("%02d", minutes).replace(" ", "0");
                    String toastText = ("Alarm set for " + hourOfDay + ":" + minutesString);
                    Toast alarmSuccessToast = Toast.makeText(toastContext, toastText, toastDuration);
                    alarmSuccessToast.show();
                }
            }
        }, 7, 0, true);
        timePickerDialog.show();
    }

    public void clearSSAlarm(View view) {
        if (sendMessage("CLEAR#SS")){
            setSwitches();
            Context toastContext = getApplicationContext();
            int toastDuration = Toast.LENGTH_SHORT;
            String toastText = ("Weekday Alarm cancelled");
            Toast alarmCancelToast = Toast.makeText(toastContext, toastText, toastDuration);
            alarmCancelToast.show();
        }
    }

    public void resetRouter(View view) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setMessage("Reset router?")
                .setTitle("Warning")
                .setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        sendMessage("reset_router");
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        // CANCEL
                    }
                });
        // Create the AlertDialog object and return it
        builder.create();
        builder.show();
    }

    public void setBrightness(int brightness) {
        String new_brightness = "BRIGHTNESS#" + brightness;
        if (sendMessage(new_brightness)){
            setSwitches();
        }
    }

    public void setVolume(int volume) {
        String new_volume = "VOLUME#" + volume;
        if (sendMessage(new_volume)){
            setSwitches();
        }
    }

    @Override
    public boolean dispatchKeyEvent(KeyEvent event){
        int keyCode = event.getKeyCode();
        if (event.getAction() == KeyEvent.ACTION_DOWN &&
                (keyCode == KeyEvent.KEYCODE_VOLUME_UP || keyCode == KeyEvent.KEYCODE_VOLUME_DOWN)){
            int new_volume;
            if (keyCode == KeyEvent.KEYCODE_VOLUME_UP) {
                new_volume = radio_volume + 1;
                if (new_volume <= 6){
                    setVolume(new_volume);
                }
            }

            else {
                new_volume = radio_volume - 1;
                if (new_volume >= 0){
                    setVolume(new_volume);
                }
            }
            return true;
        }
        else {
            return super.dispatchKeyEvent(event);
        }
    }

}
