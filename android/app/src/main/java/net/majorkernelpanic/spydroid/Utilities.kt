package net.majorkernelpanic.spydroid

import java.net.NetworkInterface
import java.net.SocketException
import java.util.regex.Pattern
import java.util.regex.PatternSyntaxException

/**
 * Licensed under the GNU LESSER GENERAL PUBLIC LICENSE, version 2.1, dated February 1999.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the latest version of the GNU Lesser General
 * Public License as published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program (LICENSE.txt); if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */
/**
 * This class provides a variety of basic utility methods that are not
 * dependent on any other classes within the org.jamwiki package structure.
 */
object Utilities {
    private var VALID_IPV4_PATTERN: Pattern? = null
    private var VALID_IPV6_PATTERN: Pattern? = null
    private const val ipv4Pattern =
        "(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.){3}([01]?\\d\\d?|2[0-4]\\d|25[0-5])"
    private const val ipv6Pattern = "([0-9a-f]{1,4}:){7}([0-9a-f]){1,4}"

    /**
     * Determine if the given string is a valid IPv4 or IPv6 address.  This method
     * uses pattern matching to see if the given string could be a valid IP address.
     *
     * @param ipAddress A string that is to be examined to verify whether or not
     * it could be a valid IP address.
     * @return `true` if the string is a value that is a valid IP address,
     * `false` otherwise.
     */
    fun isIpAddress(ipAddress: String?): Boolean {
        val m1 = VALID_IPV4_PATTERN!!.matcher(ipAddress as CharSequence)
        if (m1.matches()) {
            return true
        }
        val m2 = VALID_IPV6_PATTERN!!.matcher(ipAddress as CharSequence)
        return m2.matches()
    }

    fun isIpv4Address(ipAddress: String?): Boolean {
        val m1 = VALID_IPV4_PATTERN!!.matcher(ipAddress as CharSequence)
        return m1.matches()
    }

    fun isIpv6Address(ipAddress: String?): Boolean {
        val m1 = VALID_IPV6_PATTERN!!.matcher(ipAddress as CharSequence)
        return m1.matches()
    }

    /**
     * Returns the IP address of the first configured interface of the device
     * @param removeIPv6 If true, IPv6 addresses are ignored
     * @return the IP address of the first configured interface or null
     */
	@JvmStatic
	fun getLocalIpAddress(removeIPv6: Boolean): String? {
        try {
            val en = NetworkInterface.getNetworkInterfaces()
            while (en.hasMoreElements()) {
                val intf = en.nextElement()
                val enumIpAddr = intf.inetAddresses
                while (enumIpAddr.hasMoreElements()) {
                    val inetAddress = enumIpAddr.nextElement()
                    if (inetAddress.isSiteLocalAddress &&
                        !inetAddress.isAnyLocalAddress &&
                        (!removeIPv6 || isIpv4Address(inetAddress.hostAddress.toString()))
                    ) {
                        return inetAddress.hostAddress.toString()
                    }
                }
            }
        } catch (ignore: SocketException) {
        }
        return null
    }

    init {
        try {
            VALID_IPV4_PATTERN = Pattern.compile(ipv4Pattern, Pattern.CASE_INSENSITIVE)
            VALID_IPV6_PATTERN = Pattern.compile(ipv6Pattern, Pattern.CASE_INSENSITIVE)
        } catch (e: PatternSyntaxException) {
            //logger.severe("Unable to compile pattern", e);
        }
    }
}