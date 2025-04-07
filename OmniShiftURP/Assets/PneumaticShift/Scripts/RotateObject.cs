using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RotateObject : MonoBehaviour
{
    public float startRotation;
    public float rotationSpeed;
    public Vector3 rotationAxis;

    // Start is called before the first frame update
    void Start()
    {
        this.transform.rotation = transform.rotation * Quaternion.Euler(rotationAxis * startRotation);
    }

    // Update is called once per frame
    void Update()
    {
        this.transform.Rotate(rotationSpeed * rotationAxis * Time.deltaTime, Space.Self);
    }
}
