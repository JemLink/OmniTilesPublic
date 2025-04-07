using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerHealth : MonoBehaviour
{
    public int healthPoints;
    public float blinkDuration;
    public float blinkInterval;

    public ParticleSystem explosionParticles;

    bool exploded = false;
    public bool invincible = true;
    Color blockingColor = Color.red;

    // Start is called before the first frame update
    void Awake()
    {
        invincible = true;
        StartCoroutine(Blinking(0.2f, 3.0f));
        StartCoroutine(StartInvincibility());
    }

    // Update is called once per frame
    void Update()
    {
        CheckForFieldCollision();
    }

    public void GetDamage(int damage)
    {
        healthPoints -= damage;
        StartCoroutine(Blinking(blinkInterval, blinkDuration));

        if(healthPoints <= 0)
        {
            // Destroy player
            DestroyPlayer();
        }
    }


    private void DestroyPlayer()
    {
        //maybe play some animation
        
        StopAllCoroutines();
        StartCoroutine(DestroyPlayerCoroutine());
    }


    private void CheckForFieldCollision()
    {
        if (!exploded && !invincible)
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
                            exploded = true;
                            DestroyPlayer();
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

        if (col[index] < threshold)
        {
            return -1;
        }

        return index;
    }


    IEnumerator Blinking(float blinkInterval, float blinkDuration)
    {
        float startTime = Time.time;

        while(Time.time - startTime < blinkDuration)
        {
            Debug.Log("Should blink");
            gameObject.GetComponentInChildren<Renderer>().enabled = !gameObject.GetComponentInChildren<Renderer>().enabled;
            yield return new WaitForSeconds(blinkInterval);
        }

        gameObject.GetComponentInChildren<Renderer>().enabled = true;
    }

    IEnumerator DestroyPlayerCoroutine()
    {
        explosionParticles.Play();

        GetComponentInChildren<Renderer>().enabled = false;

        yield return new WaitUntil(() => !explosionParticles.isPlaying);

        Debug.Log("SHould explode");

        Destroy(gameObject);
    }

    IEnumerator StartInvincibility()
    {
        yield return new WaitForSecondsRealtime(3.0f);
        invincible = false;
    }
}
