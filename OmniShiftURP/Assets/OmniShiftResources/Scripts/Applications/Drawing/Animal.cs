using System.Collections;
using System.Collections.Generic;
using UnityEngine;
//using System.Linq;
//using System;

public class Animal : MonoBehaviour
{

    public bool active = true;
    int roundsWithoutHit = 0;
    public int maxRoundsWithoutHit;

    public enum Habitat { Flowers, Grass, Water, DrySoil }

    [Header("Terrain and habitat variables")]
    public Habitat myHabitat;
    public Color habitatColor;

    [Header("Movement")]
    public float speed = 3.0f;
    public float rotationSpeed;
    private Vector3 randomTargetPoint = Vector3.zero;
    public Vector2 movementRange;



    [Header("Animation")]
    private Animator anim;
    public float animationSpeed;

    public int tileID = -1;

    public Animal(Habitat habitat)
    {
        myHabitat = habitat;
    }

    public Animal(Habitat habitat, float speed)
    {
        myHabitat = habitat;
        this.speed = speed;
    }


    //private void OnDestroy()
    //{
    //    List<string> animals = new List<string>();
    //    if(InstantiateAnimals.Instance.destroyedTilesWithAnimalsPos.TryGetValue(tileID, out animals))
    //    {
    //        animals.Add(prefabName);
    //        InstantiateAnimals.Instance.destroyedTilesWithAnimalsPos[tileID] = animals;
    //    }
    //    else
    //    {
    //        animals.Add(prefabName);
    //        InstantiateAnimals.Instance.destroyedTilesWithAnimalsPos.Add(tileID, animals);
    //    }
        
    //}


    // Start is called before the first frame update
    void Start()
    {
        anim = GetComponentInChildren<Animator>();
        randomTargetPoint = transform.position;
        StartCoroutine(ChangeTargetPoint(movementRange.x, movementRange.y, 0.0f));
        active = true;
    }


    // Update is called once per frame
    void Update()
    {
        MoveRandom();
    }


    public void Move()
    {
        // not implemented yet
    }


    private void MoveRandom()
    {
        MoveTowards(randomTargetPoint);
    }


    private void MoveTowards(Vector3 point)
    {
        float step = speed * Time.deltaTime;

        transform.position = Vector3.MoveTowards(transform.position, point, step);

        if (anim)
        {
            float speed = Vector3.Distance(transform.position, point) * animationSpeed;
            anim.SetFloat("Speed", speed);
        }

        Debug.DrawLine(transform.position, point, Color.magenta);

        RotateTowards(point);
    }


    private void RotateTowards(Vector3 targetPoint)
    {
        if (Vector3.Distance(transform.position, targetPoint) > 0.05)
        {
            Quaternion targetRotation = Quaternion.identity;

            float step = rotationSpeed;
            Vector3 targetDirection = (targetPoint - transform.position).normalized;

            //Debug.Log("TargetDirection: " + targetDirection);

            targetRotation = Quaternion.LookRotation(targetDirection, -Vector3.forward);
            transform.rotation = Quaternion.RotateTowards(transform.rotation, targetRotation, step);
        }
    }


    /// <summary>
    /// Todo: rewrite this to uvs of habitat color
    /// - take a random value around the animal and check its color via raycast
    /// - move there if color fits
    /// </summary>
    /// <param name="xRange"></param>
    /// <param name="yRange"></param>
    /// <param name="zRange"></param>
    /// <returns></returns>
    IEnumerator ChangeTargetPoint(float xRange, float yRange, float zRange)
    {
        while (true)
        {
            if (active)
            {
                var Ray = new Ray(transform.position, Vector3.forward);
                RaycastHit hit;
                if (Physics.Raycast(Ray, out hit))
                {
                    if (!hit.transform.GetComponentInChildren<TileShape>())
                    {
                        SetActiveTo(false);
                        continue;
                    }
                    else
                    {
                        tileID = hit.transform.GetComponentInChildren<TileShape>().id;
                    }
                    
                }

                if(roundsWithoutHit >= maxRoundsWithoutHit)
                {
                    Debug.Log("Should set inactive: " + transform.name);
                    SetActiveTo(false);
                    continue;
                }

                roundsWithoutHit++;

                for (int i = 0; i < 20; i++)
                {
                    float x = Random.Range(-xRange, xRange);
                    float y = Random.Range(-yRange, yRange);
                    float z = 0.0f; Random.Range(-zRange, zRange);

                    Vector3 samplePoint = transform.position + (new Vector3(x, y, z));
                    Debug.DrawLine(transform.position, samplePoint, Color.blue);

                    Ray = new Ray(samplePoint, Vector3.forward);
                    //RaycastHit hit;
                    if (Physics.Raycast(Ray, out hit))
                    {
                        //TileShape tile = transform.GetComponentInChildren<TileShape>();
                        //if (tile)
                        //{
                        //    tileID = tile.id;
                        //}

                        Renderer rend = hit.transform.GetComponentInChildren<Renderer>();
                        MeshCollider col = hit.collider as MeshCollider;


                        if (rend && rend.material != null && rend.material.GetTexture("_BaseMap") != null && col)
                        {
                            Texture2D tex = rend.material.GetTexture("_BaseMap") as Texture2D;
                            Vector2 pixelUV = hit.textureCoord;
                            pixelUV.x *= tex.width;
                            pixelUV.y *= tex.height;

                            Color hitColor = tex.GetPixel((int)pixelUV.x, (int)pixelUV.y);

                            int hitMaxCol = GetMaxIndexOfColor(hitColor);
                            int habitatMaxCol = GetMaxIndexOfColor(habitatColor);



                            if (hitMaxCol == habitatMaxCol)
                            {
                                roundsWithoutHit = 0;
                                randomTargetPoint = new Vector3(hit.point.x, hit.point.y, randomTargetPoint.z);
                                break;
                            }

                        }

                    }
                }



            }
            else
            {
                var Ray = new Ray(transform.position, Vector3.forward);
                RaycastHit hit;
                if (Physics.Raycast(Ray, out hit))
                {
                    if (hit.transform.GetComponentInChildren<TileShape>())
                    {
                        Renderer rend = hit.transform.GetComponentInChildren<Renderer>();
                        MeshCollider col = hit.collider as MeshCollider;


                        if (rend && rend.material != null && rend.material.GetTexture("_BaseMap") != null && col)
                        {
                            Texture2D tex = rend.material.GetTexture("_BaseMap") as Texture2D;
                            Vector2 pixelUV = hit.textureCoord;
                            pixelUV.x *= tex.width;
                            pixelUV.y *= tex.height;

                            Color hitColor = tex.GetPixel((int)pixelUV.x, (int)pixelUV.y);

                            int hitMaxCol = GetMaxIndexOfColor(hitColor);
                            int habitatMaxCol = GetMaxIndexOfColor(habitatColor);



                            if (hitMaxCol == habitatMaxCol)
                            {
                                roundsWithoutHit = 0;
                                SetActiveTo(true);
                            }
                        }
                    }

                }
            }

            yield return new WaitForSeconds(Random.Range(0.5f, 1.6f));


        }

    }


    public void SetActiveTo(bool active)
    {
        this.active = active;
        this.GetComponentInChildren<Renderer>().enabled = active;

        if (!active)
        {
            InstantiateAnimals.Instance.destroyedAnimals.Add(this);
        }
        
    }


    private int GetMaxIndexOfVector3(Vector3 vec)
    {
        float max = -Mathf.Infinity;
        int index = -1;

        for(int i = 0; i < 3; i++)
        {
            if(vec[i] > max)
            {
                index = i;
                max = vec[i];
            }
        }

        return index;
    }

    private int GetMaxIndexOfColor(Color col)
    {
        float max = -Mathf.Infinity;
        int index = -1;

        if(col.r == col.g && col.g == col.b)
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

        return index;
    }


    /// <summary>
    /// This return the first pixels coordinates of the searched color if color exists and (-1,-1) otherwise
    /// </summary>
    /// <param name="col"></param>
    /// <param name="tex"></param>
    /// <returns></returns>
    //private Vector2 GetRandomUVWithColor(Color col, Texture2D tex)
    //{
    //    if (tex)
    //    {
    //        Color[] colors = tex.GetPixels();
    //        int width = tex.width;
    //        int height = tex.height;

    //        if (colors.Contains<Color>(col))
    //        {
    //            int index = Array.IndexOf(colors, col);
    //            int w = index % width;
    //            int h = index / height;

    //            return new Vector2(w, h);
    //        }
    //    }

    //    return new Vector2(-1.0f, -1.0f);
    //}
}
