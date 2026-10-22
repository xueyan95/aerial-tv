package app.orchard.tv

import android.app.Activity
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.UserManager
import android.view.Gravity
import android.view.WindowManager
import android.widget.TextView

/** HOME before user unlock: never touches credential-encrypted preferences or Compose state. */
class BootHomeActivity : Activity() {
    private val handler = Handler(Looper.getMainLooper())
    private var forwarded = false
    private val checkUnlock = object : Runnable {
        override fun run() {
            val unlocked = Build.VERSION.SDK_INT < 24 ||
                getSystemService(UserManager::class.java).isUserUnlocked
            if (unlocked) {
                if (!forwarded) {
                    forwarded = true
                    startActivity(Intent(this@BootHomeActivity, MainActivity::class.java)
                        .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP))
                    finish()
                }
            } else handler.postDelayed(this, 250)
        }
    }
    private val unlocked = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            handler.removeCallbacks(checkUnlock)
            handler.post(checkUnlock)
        }
    }
    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        window.addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)
        window.decorView.setBackgroundColor(Color.BLACK)
        setContentView(TextView(this).apply {
            text = getString(R.string.boot_preparing)
            textSize = 28f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        })
        if (Build.VERSION.SDK_INT >= 24) registerReceiver(unlocked, IntentFilter(Intent.ACTION_USER_UNLOCKED))
        handler.post(checkUnlock)
    }
    override fun onDestroy() {
        handler.removeCallbacks(checkUnlock)
        if (Build.VERSION.SDK_INT >= 24) runCatching { unregisterReceiver(unlocked) }
        super.onDestroy()
    }
}
