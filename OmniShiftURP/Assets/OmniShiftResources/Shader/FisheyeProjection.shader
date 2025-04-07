/******************************************************************************************
	Fisheye Projection Shader for Baloonigen, OmniProCamLight and OmniProCam Project
	Created on 2018/09/05 by SATOToshiki@TokyoTech
******************************************************************************************/

Shader "Projection/FisheyeProjection"
{
	Properties{
		_MainTex("Texture", 2D) = "white" {}
		_k1("k1", Float) = -0.05487021301558282 // -0.2971244			// k1-k3: fisheye lens distortion parameters(calculated by camera calibration using fisheye camera model)
		_k2("k2", Float) = -0.032563098607785924 // 0.08356049
		_k3("k3", Float) = 0.052556151896156436 // -0.004746397
		_k4("k4", Float) = -0.035097531887265956 // 0.00008150165
		_cx("cx", Float) = 0.0						// image plane offsetX
		_cy("cy", Float) = 0.0						// image plane offsetY
		_focalLength("f", Float) = 1.0		// f = 1.0 means that vertices are projected on a normalized image coordinate plane(z = 1 plane)
	}
		SubShader{
		Tags{ "RenderType" = "Opaque" }
		LOD 100
		Cull off

		Pass{

		CGPROGRAM
#pragma vertex vertMFVP
//#pragma vertex vertFMVP
#pragma fragment frag

#include "UnityCG.cginc"

		struct appdata {
		float4 vertex : POSITION;
		float2 uv : TEXCOORD0;
	};

	struct v2f {
		float2 uv : TEXCOORD0;
		float4 vertex : SV_POSITION;
	};

	sampler2D _MainTex;
	float4 _MainTex_ST;
	float _k1, _k2, _k3, _k4;
	float _cx, _cy;
	float _focalLength;

	/* Model -> Fisheye -> View -> Projection */
	v2f vertMFVP(appdata v) {

		v2f o;
		v.vertex.y+= _focalLength;
		float3 mProjected = mul(unity_ObjectToWorld, v.vertex);
		float3 srcNormalized = normalize(mProjected);
		float length = sqrt(srcNormalized.x * srcNormalized.x + srcNormalized.z * srcNormalized.z);
		float theta = atan2(length, srcNormalized.y);
		float theta2 = theta * theta;       // theta^2
		float theta4 = theta2 * theta2;     // theta^4
		float theta6 = theta4 * theta2;     // theta^6
		float theta8 = theta4 * theta4;     // theta^8
		float thetaD = theta * (_focalLength + _k1 * theta2 + _k2 * theta4 + _k3 * theta6 + _k4 * theta8);
		float r = _focalLength * tan(theta);
		o.vertex =
			mul(UNITY_MATRIX_P,
				mul(UNITY_MATRIX_V,
					float4(
						thetaD / r * (_focalLength * mProjected.x) / mProjected.y,
						0.0f,
						thetaD / r * (_focalLength * mProjected.z) / mProjected.y,
						1.0f
						)
				) + float4(_cx, _cy, 0, 0)
			);
		o.uv = TRANSFORM_TEX(v.uv, _MainTex);
		return o;
	}
	
	fixed4 frag(v2f i) : SV_Target{
		return tex2D(_MainTex, i.uv);
	}

	/* Fisheye -> MVP */
	v2f vertFMVP(appdata v) {
		v2f o;
		v.vertex.y += _focalLength;
		float3 srcNormalized = normalize(v.vertex.xyz);
		float length = sqrt(srcNormalized.x * srcNormalized.x + srcNormalized.z * srcNormalized.z);
		float theta = atan2(length, srcNormalized.y);
		float theta2 = theta * theta;       // theta^2
		float theta4 = theta2 * theta2;     // theta^4
		float theta6 = theta4 * theta2;     // theta^6
		float theta8 = theta4 * theta4;     // theta^8
		float thetaD = theta * (_focalLength + _k1 * theta2 + _k2 * theta4 + _k3 * theta6 + _k4 * theta8);
		float r = _focalLength * tan(theta);

		o.vertex = UnityObjectToClipPos(float4(thetaD / r * (_focalLength * v.vertex.x) / v.vertex.y, 0.0f, thetaD / r * (_focalLength * v.vertex.z) / v.vertex.y, 1.0f));	// 1.0: focal length for projection to normalized image coordinates
		o.uv = TRANSFORM_TEX(v.uv, _MainTex);
		return o;
	}
		ENDCG
	}
	}
}