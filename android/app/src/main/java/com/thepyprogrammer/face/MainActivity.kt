package com.thepyprogrammer.face

import android.Manifest
import android.app.Activity
import android.content.Context
import android.graphics.BitmapFactory
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.inputmethod.InputMethodManager
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.thepyprogrammer.face.R
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.google.android.gms.vision.CameraSource
import com.google.android.material.snackbar.Snackbar
import com.thepyprogrammer.face.camera.CameraSourcePreview
import com.thepyprogrammer.face.camera.GraphicOverlay
import kotlinx.android.synthetic.main.activity_main.*


class MainActivity : AppCompatActivity() {

    private val mCameraSource: CameraSource? = null

    private val mPreview: CameraSourcePreview? = null
    private val mGraphicOverlay: GraphicOverlay? = null

    private val RC_HANDLE_GMS = 9001

    // permission request codes need to be < 256
    private val RC_HANDLE_CAMERA_PERM = 2


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (! Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        val py = Python.getInstance()
        val module = py.getModule("plot")

        val bytes = module.callAttr("plot", "0", "0")
                    .toJava(ByteArray::class.java)
        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
        //imageView.setImageBitmap(bitmap)

        currentFocus?.let {
            (getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager)
                .hideSoftInputFromWindow(it.windowToken, 0)
        }
    }

    /**
     * Handles the requesting of the camera permission.  This includes
     * showing a "Snackbar" message of why the permission is needed then
     * sending the request.
     */
    private fun requestCameraPermission() {
        Log.w("Camera", "Camera permission is not granted. Requesting permission")
        val permissions = arrayOf<String>(Manifest.permission.CAMERA)
        if (!ActivityCompat.shouldShowRequestPermissionRationale(
                this,
                Manifest.permission.CAMERA
            )
        ) {
            ActivityCompat.requestPermissions(this, permissions, RC_HANDLE_CAMERA_PERM)
            return
        }
        val thisActivity: Activity = this
        val listener = View.OnClickListener {
            ActivityCompat.requestPermissions(
                thisActivity, permissions,
                RC_HANDLE_CAMERA_PERM
            )
        }

        Snackbar.make(
            mGraphicOverlay, R.string.permission_camera_rationale,
            Snackbar.LENGTH_INDEFINITE
        )
            .setAction(R.string.ok, listener)
            .show()
    }
}