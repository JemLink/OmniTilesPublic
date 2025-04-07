using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GravityOrbit : MonoBehaviour
{
    public float gravity;

    public bool fixedDirection;
    public Vector3 gravityDirection;

    public Camera capturingCam;
    public Vector3 toCamDirection;


    private void Start()
    {
        if (!capturingCam)
        {
            capturingCam = GameObject.FindGameObjectWithTag("SceneCam").GetComponent<Camera>();
        }
        toCamDirection = capturingCam.transform.position - transform.position;
        toCamDirection.x = 0;
        toCamDirection.y = 0;
        toCamDirection = toCamDirection.normalized;
        this.tag = "GravityField";
    }

    private void OnTriggerEnter(Collider other)
    {
        GravityAffected[] scriptsAffectedByGravity = other.GetComponentsInChildren<GravityAffected>();
        //Debug.Log("Collided with " + other.gameObject.name);
        for (int i = 0; i < scriptsAffectedByGravity.Length; i++)
        {
            scriptsAffectedByGravity[i].gravityField = this;
        }
        
    }


    public Vector3 GravityDirection(Vector3 movementDirection, Vector3 objectPosition)
    {
        if (fixedDirection)
        {
            return gravityDirection;
        }

        Vector3 gravityUp = (objectPosition - transform.position).normalized;

        Vector3 xDirection = (Vector3.Cross(gravityUp, toCamDirection)).normalized;

        Vector3 yDirection = (Vector3.Cross(gravityUp, xDirection)).normalized;


        return xDirection * movementDirection.x + yDirection * -movementDirection.y;
    }
}
