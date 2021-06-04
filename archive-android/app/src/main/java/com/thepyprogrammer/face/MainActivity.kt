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
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.google.android.gms.vision.CameraSource
import com.google.android.gms.vision.Detector
import com.google.android.gms.vision.MultiProcessor
import com.google.android.gms.vision.Tracker
import com.google.android.gms.vision.face.Face
import com.google.android.material.snackbar.Snackbar
import com.thepyprogrammer.face.R
import com.thepyprogrammer.face.camera.CameraSourcePreview
import com.thepyprogrammer.face.camera.FaceGraphic
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

    //==============================================================================================
    // Graphic Face Tracker
    //==============================================================================================

    //==============================================================================================
    // Graphic Face Tracker
    //==============================================================================================
    /**
     * Factory for creating a face tracker to be associated with a new face.  The multiprocessor
     * uses this factory to create face trackers as needed -- one for each individual.
     */
    private class GraphicFaceTrackerFactory : MultiProcessor.Factory<Face> {
        override fun create(face: Face): Tracker<Face?> {
            return GraphicFaceTracker(mGraphicOverlay)
        }
    }

    /**
     * Face tracker for each detected individual. This maintains a face graphic within the app's
     * associated face overlay.
     */
    private class GraphicFaceTracker internal constructor(private val mOverlay: GraphicOverlay) :
        Tracker<Face?>() {
        private val mFaceGraphic: FaceGraphic = FaceGraphic(mOverlay)

        /**
         * Start tracking the detected face instance within the face overlay.
         */
        override fun onNewItem(faceId: Int, item: Face?) {
            mFaceGraphic.setId(faceId)
        }

        /**
         * Update the position/characteristics of the face within the overlay.
         */
        override fun onUpdate(detectionResults: Detector.Detections<Face?>?, face: Face?) {
            mOverlay.add(mFaceGraphic)
            mFaceGraphic.updateFace(face)
        }

        /**
         * Hide the graphic when the corresponding face was not detected.  This can happen for
         * intermediate frames temporarily (e.g., if the face was momentarily blocked from
         * view).
         */
        override fun onMissing(detectionResults: Detector.Detections<Face?>?) {
            mOverlay.remove(mFaceGraphic)
        }

        /**
         * Called when the face is assumed to be gone for good. Remove the graphic annotation from
         * the overlay.
         */
        override fun onDone() {
            mOverlay.remove(mFaceGraphic)
        }

    }
}