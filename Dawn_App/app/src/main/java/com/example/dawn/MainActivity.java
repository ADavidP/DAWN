package com.example.dawn;

import android.app.AlertDialog;
import android.app.TimePickerDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.NetworkCapabilities;
import android.os.Build;
import android.os.StrictMode;

import androidx.annotation.ColorInt;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import androidx.appcompat.widget.SwitchCompat;
import androidx.appcompat.widget.Toolbar;
import androidx.core.content.res.ResourcesCompat;

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
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

@RequiresApi(api = Build.VERSION_CODES.JELLY_BEAN)
public class MainActivity extends AppCompatActivity {

    public static final String COLOUR = "colour";
    public static final String NEW_COLOUR = "new_colour";
    TimePickerDialog timePicker;
    SeekBar brightnessSlider;
    SeekBar volumeSlider;

    Boolean stereoOn;
    Boolean bedroomSpeakersOn;
    Boolean livingRoomSpeakersOn;
    Boolean spotifyClientOn;
    Short volume;
    Short radioStation;
    Boolean bedroomLightsOn;
    Boolean livingRoomLightsOn;
    Boolean officeLightsOn;
    Boolean kitchenLightsOn;
    Boolean partyMode;
    Short brightness;

    Boolean isNewColour;
    String newColourString;

    Integer redPigment;
    Integer greenPigment;
    Integer bluePigment;
    @ColorInt
    Integer colour;

    Boolean weekdayAlarmOn;
    Short weekdayAlarmHours;
    Short weekdayAlarmMinutes;
    Boolean weekendAlarmOn;
    Short weekendAlarmHours;
    Short weekendAlarmMinutes;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitNetwork().build();
        StrictMode.setThreadPolicy(policy);
        setContentView(R.layout.activity_main);

        Intent intent = getIntent();
        if (intent != null && intent.getExtras() != null && intent.getExtras().containsKey(NEW_COLOUR)){
            isNewColour = true;
            colour = intent.getIntExtra(NEW_COLOUR, getColor(R.color.warm_glow));
            redPigment = Color.red(colour);
            greenPigment = Color.green(colour);
            bluePigment = Color.blue(colour);

            String redPigmentString = ("00" + Integer.toHexString(redPigment)).substring(Integer.toHexString(redPigment).length());
            String greenPigmentString = ("00" + Integer.toHexString(greenPigment)).substring(Integer.toHexString(greenPigment).length());
            String bluePigmentString = ("00" + Integer.toHexString(bluePigment)).substring(Integer.toHexString(bluePigment).length());
            newColourString = "COLOUR#" + redPigmentString + greenPigmentString + bluePigmentString;
        }
        else {
            isNewColour = false;
        }

        Toolbar myToolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(myToolbar);
        brightnessSlider = findViewById(R.id.brightness);

        brightnessSlider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                if (b) {setBrightness (i);}
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        volumeSlider = findViewById(R.id.volume);

        volumeSlider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                if (b) {setVolume (i);}
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

    public static boolean isWifiConnected(Context context) {
        ConnectivityManager cm = (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
            if (cm == null) {
                return false;
            }
            else {
                NetworkCapabilities capabilities = cm.getNetworkCapabilities(cm.getActiveNetwork());
                if (capabilities == null) {
                    return false;
                }
                else {
                    return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI);
                }
            }
    }

    @Override
    protected void onResume () {
        super.onResume();
        if (isWifiConnected(this))
        {
            try {
                Socket socket = new Socket("192.168.1.214", 12345);
                PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
                byte[] response = new byte[21];
                InputStream in = socket.getInputStream();
                if (isNewColour) {
                    out.println(newColourString);
                    isNewColour = false;
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

    private void processResponse (byte [] response) {
        stereoOn = Byte.toUnsignedInt(response[0]) == 1;
        bedroomSpeakersOn = Byte.toUnsignedInt(response[1]) == 1;
        livingRoomSpeakersOn = Byte.toUnsignedInt(response[2]) == 1;
        spotifyClientOn = Byte.toUnsignedInt(response[3]) == 1;
        volume = (short) Byte.toUnsignedInt(response[4]);
        radioStation = (short) Byte.toUnsignedInt(response[5]);
        bedroomLightsOn = Byte.toUnsignedInt(response[6]) == 1;
        livingRoomLightsOn = Byte.toUnsignedInt(response[7]) == 1;
        officeLightsOn = Byte.toUnsignedInt(response[8]) == 1;
        kitchenLightsOn = Byte.toUnsignedInt(response[9]) == 1;
        partyMode = Byte.toUnsignedInt(response[10]) == 1;
        brightness = (short) Byte.toUnsignedInt(response[11]);
        redPigment = Byte.toUnsignedInt(response[12]);
        greenPigment = Byte.toUnsignedInt(response[13]);
        bluePigment = Byte.toUnsignedInt(response[14]);
        weekdayAlarmOn = Byte.toUnsignedInt(response[15]) == 1;
        weekdayAlarmHours = (short) Byte.toUnsignedInt(response[16]);
        weekdayAlarmMinutes = (short) Byte.toUnsignedInt(response[17]);
        weekendAlarmOn = Byte.toUnsignedInt(response[18]) == 1;
        weekendAlarmHours = (short) Byte.toUnsignedInt(response[19]);
        weekendAlarmMinutes = (short) Byte.toUnsignedInt(response[20]);
    }

    @RequiresApi(api = Build.VERSION_CODES.JELLY_BEAN)
    private void setSwitches () {
        SwitchCompat stereoSwitch = findViewById(R.id.stereo_switch);
        stereoSwitch.setChecked(stereoOn);

        SwitchCompat bedroomSpeakers = findViewById(R.id.bedroom_speakers);
        bedroomSpeakers.setChecked(bedroomSpeakersOn);

        SwitchCompat livingRoomSpeakers = findViewById(R.id.living_room_speakers);
        livingRoomSpeakers.setChecked(livingRoomSpeakersOn);

        volumeSlider = findViewById(R.id.volume);
        volumeSlider.setMax(6);
        volumeSlider.setProgress(volume);

        ImageView[] stations = {
                findViewById(R.id.fip),
                findViewById(R.id.fip_electro),
                findViewById(R.id.triplej),
                findViewById(R.id.folk_forward),
                findViewById(R.id.gaydio),
                findViewById(R.id.bbc6),
                findViewById(R.id.seven_inch_soul),
                findViewById(R.id.heavyweight_reggae)
        };

        for (int i = 0; i < stations.length; i++) {
            if (radioStation == i + 1) {
                stations[i].setBackground(ResourcesCompat.getDrawable(this.getResources(),
                        R.drawable.border,
                        null));
            }
            else {
                stations[i].setBackground(null);
            }
        }

        if (spotifyClientOn) {
            findViewById(R.id.spotify).setBackground(ResourcesCompat.getDrawable(this.getResources(),
                    R.drawable.border,
                    null));
        }
        else {
            findViewById(R.id.spotify).setBackground(null);
        }

        SwitchCompat bedroomLights = findViewById(R.id.bedroom_lights);
        bedroomLights.setChecked(bedroomLightsOn);

        SwitchCompat livingRoomLights = findViewById(R.id.living_room_lights);
        livingRoomLights.setChecked(livingRoomLightsOn);

        SwitchCompat officeLights = findViewById(R.id.office_lights);
        officeLights.setChecked(officeLightsOn);

        SwitchCompat kitchenLights = findViewById(R.id.kitchen_lights);
        kitchenLights.setChecked(kitchenLightsOn);

        SwitchCompat partyModeSwitch = findViewById(R.id.party_mode);
        partyModeSwitch.setChecked(partyMode);

        brightnessSlider = findViewById(R.id.brightness);
        brightnessSlider.setMax(63);
        brightnessSlider.setProgress(brightness);
        if (weekdayAlarmOn) {
            findViewById(R.id.clear_time_weekday).setVisibility(View.VISIBLE);
            TextView mfTime = findViewById(R.id.weekday_time);
            mfTime.setVisibility(View.VISIBLE);
            String minutesString = String.format(Locale.ENGLISH, "%02d", weekdayAlarmMinutes);
            String alarmTime = weekdayAlarmHours + ":" + minutesString;
            mfTime.setText(alarmTime);
        }
        else {
            findViewById(R.id.clear_time_weekday).setVisibility(View.INVISIBLE);
            findViewById(R.id.weekday_time).setVisibility(View.INVISIBLE);
        }
        if (weekendAlarmOn) {
            findViewById(R.id.clear_time_weekend).setVisibility(View.VISIBLE);
            TextView ssTime = findViewById(R.id.weekend_time);
            ssTime.setVisibility(View.VISIBLE);
            String minutesString = String.format(Locale.ENGLISH, "%02d", weekendAlarmMinutes);
            String alarmTime = weekendAlarmHours + ":" + minutesString;
            ssTime.setText(alarmTime);
        }
        else {
            findViewById(R.id.clear_time_weekend).setVisibility(View.INVISIBLE);
            findViewById(R.id.weekend_time).setVisibility(View.INVISIBLE);
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

    public void toggleBedroomSpeakers(View view) {
        sendMessage("bedroom_speakers");
        setSwitches();
    }

    public void toggleLivingRoomSpeakers(View view) {
        sendMessage("living_room_speakers");
        setSwitches();
    }

    public void setVolume(int volume) {
        String newVolume = "VOLUME#" + volume;
        if (sendMessage(newVolume)){
            setSwitches();
        }
    }

    @Override
    public boolean dispatchKeyEvent(KeyEvent event){
        int keyCode = event.getKeyCode();
        if (event.getAction() == KeyEvent.ACTION_DOWN &&
                (keyCode == KeyEvent.KEYCODE_VOLUME_UP || keyCode == KeyEvent.KEYCODE_VOLUME_DOWN)){
            int newVolume;
            if (keyCode == KeyEvent.KEYCODE_VOLUME_UP) {
                newVolume = volume + 1;
                if (newVolume <= 6){
                    setVolume(newVolume);
                }
            }

            else {
                newVolume = volume - 1;
                if (newVolume >= 0){
                    setVolume(newVolume);
                }
            }
            return true;
        }
        else {
            return super.dispatchKeyEvent(event);
        }
    }

    public void fip (View view) {
        sendMessage("fip");
        setSwitches();
    }

    public void fipElectro(View view) {
        sendMessage("fip_electro");
        setSwitches();
    }

    public void triplej (View view) {
        sendMessage("triplej");
        setSwitches();
    }

    public void folkForward(View view) {
        sendMessage("folk_forward");
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

    public void sevenInchSoul(View view) {
        sendMessage("seven_inch_soul");
        setSwitches();
    }

    public void heavyweightReggae(View view) {
        sendMessage("heavyweight_reggae");
        setSwitches();
    }

    public void toggleSpotify(View view) {
        sendMessage("spotify");
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

    public void setBrightness(int brightness) {
        String newBrightness = "BRIGHTNESS#" + brightness;
        if (sendMessage(newBrightness)){
            setSwitches();
        }
    }

    public void colourPicker(View view) {
        colour = Color.rgb(redPigment, greenPigment, bluePigment);
        Intent intent = new Intent(this, ColourPicker.class);
        intent.putExtra(COLOUR, colour);
        startActivity(intent);
        finish();
    }

    public void setMFAlarm(View view) {
        timePicker = new TimePickerDialog(MainActivity.this, new TimePickerDialog.OnTimeSetListener() {
            @Override
            public void onTimeSet(TimePicker timePicker, int hourOfDay, int minutes) {
                String alarmText = "ALARM#MF#" + hourOfDay + ":" + minutes;
                if (sendMessage(alarmText)){
                    setSwitches();
                    Context toastContext = getApplicationContext();
                    int toastDuration = Toast.LENGTH_SHORT;
                    String minutesString = String.format(Locale.ENGLISH, "%02d", minutes).replace(" ", "0");
                    String toastText = ("Alarm set for " + hourOfDay + ":" + minutesString);
                    Toast alarmSuccessToast = Toast.makeText(toastContext, toastText, toastDuration);
                    alarmSuccessToast.show();
                }
            }
        }, 7, 0, true);
        timePicker.show();
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
        timePicker = new TimePickerDialog(MainActivity.this, new TimePickerDialog.OnTimeSetListener() {
            @Override
            public void onTimeSet(TimePicker timePicker, int hourOfDay, int minutes) {
                String alarmText = "ALARM#SS#" + hourOfDay + ":" + minutes;
                if (sendMessage(alarmText)){
                    setSwitches();
                    Context toastContext = getApplicationContext();
                    int toastDuration = Toast.LENGTH_SHORT;
                    String minutesString = String.format(Locale.ENGLISH, "%02d", minutes).replace(" ", "0");
                    String toastText = ("Alarm set for " + hourOfDay + ":" + minutesString);
                    Toast alarmSuccessToast = Toast.makeText(toastContext, toastText, toastDuration);
                    alarmSuccessToast.show();
                }
            }
        }, 7, 0, true);
        timePicker.show();
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
        builder.create();
        builder.show();
    }

}
