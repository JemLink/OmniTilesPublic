using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ProjectileBehaviour : MonoBehaviour
{
    //public GravityOrbit gravityField;
    public float timeTilDestroy;
    public float speed = 5f;
    public float turnSpeed = 0.1f;
    public int damage = 10;
    public ParticleSystem explosion;

    private Rigidbody rb;

    [Header("Field Parameters")]
    public Color blockingColor;
    private bool exploded = false;


    // Start is called before the first frame update
    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }

    // Update is called once per frame
    void Update()
    {
        MoveProjectile();
        CheckForFieldCollision();
    }


    private void DestroyProjectile()
    {
        //maybe play some animation

        StopAllCoroutines();
        Destroy(gameObject);
    }


    public void StartShoot()
    {
        StartCoroutine(StartShootCo());
    }

    private IEnumerator StartShootCo()
    {
        // move projectile with gravity field

        //destroy projectile after time for destruction
        yield return new WaitForSeconds(timeTilDestroy);

        DestroyProjectile();
    }

    private void MoveProjectile()
    {
        rb.MovePosition(transform.position + transform.forward * speed * Time.deltaTime);
    }


    private void CheckForFieldCollision()
    {
        if (!exploded)
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
                        int blockingMaxCol = GetMaxIndexOfColor(blockingColor, 0.7f);

                        if (hitMaxCol == blockingMaxCol)
                        {
                            StartCoroutine(Explode());
                        }
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
        if (other.tag.Equals("Player"))
        {
            if (!transform.parent.Equals(other.transform))
            {
                PlayerHealth pHealth = other.gameObject.GetComponent<PlayerHealth>();
                if (pHealth)
                {
                    pHealth.GetDamage(damage);
                    StartCoroutine(Explode());
                }
            }
           
        }
    }

    IEnumerator Explode()
    {
        exploded = true;
        if (explosion)
        {
            explosion.Play();
            gameObject.GetComponentInChildren<Renderer>().enabled = false;
            yield return new WaitUntil(() => explosion.isStopped);

        }

        DestroyProjectile();

    }

    //private Vector3 GravityDirection(Vector3 movementDirection)
    //{
    //    Vector3 gravityUp = (transform.position - gravityField.transform.position).normalized;

    //    Vector3 xDirection = (Vector3.Cross(gravityUp, gravityField.toCamDirection)).normalized;

    //    Vector3 yDirection = (Vector3.Cross(gravityUp, xDirection)).normalized;


    //    return xDirection * -movementDirection.x + yDirection * -movementDirection.y;
    //}
}
