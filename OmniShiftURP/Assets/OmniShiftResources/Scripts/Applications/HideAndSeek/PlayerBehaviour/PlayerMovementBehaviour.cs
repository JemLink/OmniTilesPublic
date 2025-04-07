using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerMovementBehaviour : GravityAffected
{


    [Header("Component References")]
    public Rigidbody playerRigidbody;
    public Vector3 cameraOffset;
    public Vector3 startPositionOffset;

    [Header("Movement Settings")]
    public float movementSpeed = 3f;
    public float turnSpeed = 0.1f;
    //public GravityOrbit gravityField;
    public Camera capturingCamera;


    //Stored Values
    //private Camera mainCamera;
    private Vector3 movementDirection;
    private bool onTile = false;

    [Header("Field Settings")]
    public Color slowDownColor = Color.green;
    public Color speedUpColor = Color.blue;
    public float startSpeed = 3.0f;
    public float fastSpeed = 6.0f;
    public float slowSpeed = 1.5f;
    private delegate void FunctionToCall();
    private FunctionToCall speedFunction;


    public void SetupBehaviour()
    {


    }


    new private void Start()
    {
        playerRigidbody = GetComponent<Rigidbody>();

        if (capturingCamera == null)
        {
            capturingCamera = GameObject.FindGameObjectWithTag("SceneCam").GetComponent<Camera>();
        }

        transform.parent = parent;
        //Debug.Log("Set position to: " + (capturingCamera.transform.position + cameraOffset));

        if (gravityField == null)
        {
            //Debug.Log("Attached gravity field: " + GameObject.FindGameObjectWithTag("GravityField").name);
            if (GameObject.FindGameObjectWithTag("GravityField"))
            {
                gravityField = GameObject.FindGameObjectWithTag("GravityField").GetComponent<GravityOrbit>();

            }
        }

        if (gravityField)
        {
            transform.position = gravityField.transform.position + startPositionOffset;//capturingCamera.transform.position + cameraOffset;
        }

    }



    public void UpdateMovementData(Vector3 newMovementDirection)
    {
        movementDirection = newMovementDirection;
    }

    void FixedUpdate()
    {
        MoveThePlayer();
        TurnThePlayer();

        
        CheckForColorCollision();
    }

    void MoveThePlayer()
    {
        Vector3 movement = GravityDirection(movementDirection) * movementSpeed * Time.deltaTime;
        
        if (onTile)
        {
            movement.z = 0.0f;
        }

        playerRigidbody.MovePosition(transform.position + movement);
    }

    void TurnThePlayer()
    {
        if (gravityField && movementDirection.sqrMagnitude > 0.01f)
        {
            Vector3 fieldToCam = (capturingCamera.transform.position - gravityField.transform.position).normalized;
            //Debug.Log("movement " + movementDirection);
            Quaternion rotation = Quaternion.Slerp(playerRigidbody.rotation,
                                                 Quaternion.LookRotation(GravityDirection(movementDirection), -fieldToCam),
                                                 turnSpeed);

            playerRigidbody.MoveRotation(rotation);

        }
    }




    private Vector3 GravityDirection(Vector3 movementDirection)
    {
        if (gravityField)
        {
            Vector3 gravityUp = new Vector3();
            //gravityUp = (transform.position - gravityField.transform.position).normalized;
            if (gravityField.fixedDirection)
            {
                gravityUp = (capturingCamera.transform.position - transform.position).normalized;
            }
            else
            {
                gravityUp = (transform.position - gravityField.transform.position).normalized;
            }


            Vector3 xDirection = (Vector3.Cross(gravityUp, gravityField.toCamDirection)).normalized;
            //Debug.Log("XDirection " + xDirection);
            if (xDirection.Equals(Vector3.zero))
            {
                xDirection = movementDirection;
            }

            Vector3 yDirection = (Vector3.Cross(gravityUp, xDirection)).normalized;


            return xDirection * movementDirection.x + yDirection * movementDirection.y;
        }
        else
        {
            return Vector3.zero;
        }


    }

    

    private void CheckForColorCollision()
    {
        var Ray = new Ray(transform.position, Vector3.forward);
        RaycastHit hit;
        if (Physics.Raycast(Ray, out hit))
        {
            Debug.Log("Hit: " + hit.transform.name);
            if (hit.transform.GetComponentInChildren<Paintable>())
            {
                Debug.Log("Hit tile");
                Renderer rend = hit.transform.GetComponentInChildren<Renderer>();
                MeshCollider col = hit.collider as MeshCollider;


                if (rend && rend.material != null && rend.material.GetTexture("_BaseMap") != null && col)
                {
                    Texture2D tex = rend.material.GetTexture("_BaseMap") as Texture2D;
                    Vector2 pixelUV = hit.textureCoord;
                    pixelUV.x *= tex.width;
                    pixelUV.y *= tex.height;

                    Color hitColor = tex.GetPixel((int)pixelUV.x, (int)pixelUV.y);

                    int hitMaxCol = GetMaxIndexOfColor(hitColor, 0.7f);

                    switch (hitMaxCol)
                    {
                        case -1:
                            movementSpeed = startSpeed;
                            break;
                        case 0:
                            break;
                        case 1:
                            movementSpeed = slowSpeed;
                            break;
                        case 2:
                            movementSpeed = fastSpeed;
                            break;
                            
                    }
                    
                }

            }
        }


    }


    private int GetMaxIndexOfColor(Color col, float threshold)
    {
        float max = -Mathf.Infinity;
        int index = -1;

        if (col.r == col.g && col.g == col.b)
        {
            return -1;
        }

        for (int i = 0; i < 3; i++)
        {
            if (col[i] > max)
            {
                index = i;
                max = col[i];
            }
        }

        if(col[index] < threshold)
        {
            return -1;
        }

        return index;
    }

    private void OnTriggerEnter(Collider other)
    {
        if(other.gameObject.tag == "GravityField")
        {
            onTile = true;
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (other.gameObject.tag == "GravityField")
        {
            onTile = false;
        }
    }

}
