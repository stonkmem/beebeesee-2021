package com.thepyprogrammer.face.view

import android.graphics.ImageFormat
import android.graphics.PixelFormat
import android.hardware.Camera
import android.hardware.Camera.AutoFocusCallback
import android.hardware.Camera.PreviewCallback
import android.view.SurfaceHolder
import android.view.SurfaceView


class CameraView(private val surfaceView_: SurfaceView) : SurfaceHolder.Callback {
    interface CameraReadyCallback {
        fun onCameraReady()
    }

    private var camera_: Camera? = null
    private var surfaceHolder_: SurfaceHolder? = null
    var cameraReadyCb_: CameraReadyCallback? = null
    private var supportedFrameRate: List<IntArray>? = null
    var supportedPreviewSize: List<Camera.Size>? = null
        private set
    private var procSize_: Camera.Size? = null
    fun Width(): Int {
        return procSize_!!.width
    }

    fun Height(): Int {
        return procSize_!!.height
    }

    fun setCameraReadyCallback(cb: CameraReadyCallback?) {
        cameraReadyCb_ = cb
    }

    fun StartPreview() {
        if (camera_ == null) return
        camera_!!.startPreview()
    }

    fun StopPreview() {
        if (camera_ == null) return
        camera_!!.stopPreview()
    }

    fun AutoFocus() {
        camera_!!.autoFocus(afcb)
    }

    fun Release() {
        if (camera_ != null) {
            camera_!!.stopPreview()
            camera_!!.release()
            camera_ = null
        }
    }

    fun setupCamera(wid: Int, hei: Int, bufNumber: Int, fps: Double, cb: PreviewCallback?) {
        var diff =
            Math.abs(supportedPreviewSize!![0].width * supportedPreviewSize!![0].height - wid * hei)
                .toDouble()
        var targetIndex = 0
        for (i in 1 until supportedPreviewSize!!.size) {
            val newDiff =
                Math.abs(supportedPreviewSize!![i].width * supportedPreviewSize!![i].height - wid * hei)
                    .toDouble()
            if (newDiff < diff) {
                diff = newDiff
                targetIndex = i
            }
        }
        procSize_!!.width = supportedPreviewSize!![targetIndex].width
        procSize_!!.height = supportedPreviewSize!![targetIndex].height
        diff =
            Math.abs(supportedFrameRate!![0][0] * supportedFrameRate!![0][1] - fps * fps * 1000 * 1000)
        targetIndex = 0
        for (i in 1 until supportedFrameRate!!.size) {
            val newDiff =
                Math.abs(supportedFrameRate!![i][0] * supportedFrameRate!![i][1] - fps * fps * 1000 * 1000)
            if (newDiff < diff) {
                diff = newDiff
                targetIndex = i
            }
        }
        val targetMaxFrameRate = supportedFrameRate!![targetIndex][0]
        val targetMinFrameRate = supportedFrameRate!![targetIndex][1]
        val p = camera_!!.parameters
        p.setPreviewSize(procSize_!!.width, procSize_!!.height)
        p.previewFormat = ImageFormat.NV21
        p.setPreviewFpsRange(targetMaxFrameRate, targetMinFrameRate)
        camera_!!.parameters = p
        val pixelFormat = PixelFormat()
        PixelFormat.getPixelFormatInfo(ImageFormat.NV21, pixelFormat)
        val bufSize = procSize_!!.width * procSize_!!.height * pixelFormat.bitsPerPixel / 8
        var buffer: ByteArray? = null
        for (i in 0 until bufNumber) {
            buffer = ByteArray(bufSize)
            camera_!!.addCallbackBuffer(buffer)
        }
        camera_!!.setPreviewCallbackWithBuffer(cb)
    }

    private fun initCamera() {
        camera_ = Camera.open()
        procSize_ = camera_?.Size(0, 0)
        val p = camera_?.parameters
        supportedFrameRate = p?.supportedPreviewFpsRange
        supportedPreviewSize = p?.supportedPreviewSizes
        procSize_ = supportedPreviewSize?.size?.div(2)?.let { supportedPreviewSize?.get(it) }
        procSize_?.width?.let { procSize_?.height?.let { it1 -> p?.setPreviewSize(it, it1) } }
        camera_?.parameters = p
        //camera_.setDisplayOrientation(90);
        try {
            camera_?.setPreviewDisplay(surfaceHolder_)
        } catch (ex: Exception) {
            ex.printStackTrace()
        }
        camera_?.setPreviewCallbackWithBuffer(null)
        camera_?.startPreview()
    }

    private val afcb =
        AutoFocusCallback { success, camera -> }

    override fun surfaceChanged(sh: SurfaceHolder, format: Int, w: Int, h: Int) {}
    override fun surfaceCreated(sh: SurfaceHolder) {
        initCamera()
        if (cameraReadyCb_ != null) cameraReadyCb_!!.onCameraReady()
    }

    override fun surfaceDestroyed(sh: SurfaceHolder) {
        Release()
    }

    init {
        surfaceHolder_ = surfaceView_.holder
        surfaceHolder_?.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS)
        surfaceHolder_?.addCallback(this)
    }
}