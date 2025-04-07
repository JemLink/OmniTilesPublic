using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GravityController : GravityAffected
{
    // attach to rigidbody to orbit the world

    //public GravityOrbit gravityField;
    private Rigidbody rb;
    public float rotationSpeed = 20.0f;
    public LayerMask layerMask;

    private float minHitDistance = Mathf.Infinity;

    // Start is called before the first frame update
    new void Start()
    {
        rb = GetComponent<Rigidbody>();
    }

    private void FixedUpdate()
    {
        if (gravityField)
        {
            Vector3 gravityUp = Vector3.zero;

            if (gravityField.fixedDirection)
            {
                gravityUp = -gravityField.gravityDirection;
            }
            else
            {
                gravityUp = (transform.position - gravityField.transform.position).normalized;
            }

            

            Vector3 localUp = -transform.up;
            Quaternion targetRot = Quaternion.FromToRotation(localUp, gravityUp) * transform.rotation;

            rb.MoveRotation(targetRot);

            // push down for gravity
            rb.AddForce((-gravityUp * gravityField.gravity) * rb.mass);
        }
    }
}
