using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

public class InstantiateAnimals : MonoBehaviour
{    

    [Serializable]
    public struct Animals { public Animal animal; public int numberOnTile; }
    //[Serializable]
    //public struct HabitatColor { public Animal.Habitat habitat; public Color color; }

    [Serializable]
    public struct HabitatsAnimals {
        public Animal.Habitat habitat;
        public Color habitatColor;
        public List<Animals> animalsFoundInHabitat;
    }


    public static InstantiateAnimals Instance { get; private set; }

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(this);
        }
        else
        {
            Instance = this;
        }
    }


    public List<HabitatsAnimals> habitatsWithAnimals;
    //public List<HabitatColor> habitatsColor;

    //public List<int> tilesWithAnimals;
    public Dictionary<int, List<Color>> tilesWithAnimalsOfColor = new Dictionary<int, List<Color>>();

    [Header("Animal Instantiation")]
    public Vector3 instantiationOffset;
    public Transform parent;
    public Dictionary<int, List<Animal>> destroyedTilesWithAnimalsPos = new Dictionary<int, List<Animal>>();
    public List<Animal> destroyedAnimals;
    //public List<TileShape> tiles = new List<TileShape>();


    private void OnValidate()
    {
        
    }

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }




    public void RespawnAnimalsOn(List<TileShape> tiles)
    {
        List<Animal> spawnedAnimals = new List<Animal>();
        foreach (TileShape tile in tiles)
        {
            foreach(Animal anim in destroyedAnimals)
            {
                Debug.Log("Check animal");
                if (anim.tileID == tile.id)
                {
                    Debug.Log("FOund animal to respawn");
                    anim.transform.localPosition = tile.position + instantiationOffset;
                    anim.SetActiveTo(true);
                    spawnedAnimals.Add(anim);
                } 
            }
            
        }

        foreach(Animal anim in spawnedAnimals)
        {
            destroyedAnimals.Remove(anim);
        }

    }


    public void SpawnAnimalsAt(RaycastHit hit)
    {
        TileShape tile = hit.transform.GetComponentInChildren<TileShape>();
        if (tile)
        {
            SpawnAnimals(tile, hit.point);
        }

        //var Ray = new Ray(position, Vector3.forward); // capturingCam.ScreenPointToRay(brush.transform.position);
        
        //RaycastHit hit;
        //if (Physics.Raycast(Ray, out hit))
        //{
        //    TileShape tile = hit.transform.GetComponentInChildren<TileShape>();
        //    if (tile)
        //    {
        //        SpawnAnimals(tile, hit.point);
        //    }
        //}
    }


    private void SpawnAnimals(TileShape tile, Vector3 pos)
    {
        //if (tilesWithAnimals.Contains(tile.id))
        //{
        //    Debug.Log("Already has animals");
        //    return;
        //}

        // see if tile has paintable, do not spawn otherwise
        Paintable paint = tile.GetComponentInChildren<Paintable>();
        if (paint)
        {
            //Debug.Log("Got paint");
            // check if tile has color associated with habitat of animal
            Texture2D tex = tile.GetComponentInChildren<Renderer>().material.GetTexture("_BaseMap") as Texture2D;

            foreach(HabitatsAnimals hab in habitatsWithAnimals)
            {
                //Debug.Log("Got paint");
                Color habitatCol = hab.habitatColor;

                if (tilesWithAnimalsOfColor.ContainsKey(tile.id))
                {
                    if (tilesWithAnimalsOfColor[tile.id].Contains(habitatCol))
                    {
                        //Debug.Log("Already has Color");
                        continue;
                    }
                }


                Vector2 colorUVs = GetUVsWithColor(habitatCol, tex);

                // spawn number of tile animals
                if (!colorUVs.Equals(-Vector2.one))
                {
                    foreach (Animals anim in hab.animalsFoundInHabitat)
                    {
                        StartCoroutine(SpawnAnimal(anim.animal, pos, 3.0f, anim.numberOnTile));
                        //if (!tilesWithAnimals.Contains(tile.id))
                        //{
                        //    tilesWithAnimals.Add(tile.id);
                        //}

                        if (!tilesWithAnimalsOfColor.ContainsKey(tile.id))
                        {
                            List<Color> cols = new List<Color>();
                            cols.Add(habitatCol);
                            tilesWithAnimalsOfColor.Add(tile.id, cols);
                        }
                        else
                        {
                            if (!tilesWithAnimalsOfColor[tile.id].Contains(habitatCol))
                            {
                                tilesWithAnimalsOfColor[tile.id].Add(habitatCol);
                            }
                        }
                    }
                    
                }
            }


            
            
            // the movement between tiles will be done in the animal script
            
        }
        
    }


    /// <summary>
    /// This return the first pixels coordinates of the searched color if color exists and (-1,-1) otherwise
    /// </summary>
    /// <param name="col"></param>
    /// <param name="tex"></param>
    /// <returns></returns>
    private Vector2 GetUVsWithColor(Color col, Texture2D tex)
    {
        if (tex)
        {
            Color[] colors = tex.GetPixels();
            int width = tex.width;
            int height = tex.height;

            List<Color> colorsList = new List<Color>();
            for(int i = 0; i < colors.Length; i++)
            {
                
                int colorIndex = GetMaxIndexOfColor(colors[i], 0.7f);
                switch (colorIndex)
                {
                    // colorsList.Add(colors[i]);
                    case -1:
                        //colorsList.Add(colors[i]);
                        //if (!colorsList.Contains(Color.red))
                        //{
                        //    //colorsList.Add(Color.red);
                        //}

                        break;
                    case 0:
                        // red
                        if (!colorsList.Contains(Color.red))
                        {
                            colorsList.Add(Color.red);
                        }

                        break;
                    case 1:
                        // green
                        if (!colorsList.Contains(Color.green))
                        {
                            colorsList.Add(Color.green);
                        }
                        break;
                    case 2:
                        // blue
                        if (!colorsList.Contains(Color.blue))
                        {
                            colorsList.Add(Color.blue);
                        }
                        break;
                    default:
                        Debug.Log("No color");
                        break;
                   }


                }

            colorsList = colorsList.Distinct().ToList();


            // Debug.Log("Colors " + colorsList.Count);

            if (colorsList.Contains<Color>(col))
            {
                int index = Array.IndexOf(colors, col);
                int w = index % width;
                int h = index / height;

                return new Vector2(w, h);
            }
            // Debug.Log("Did not contain color: " + col);
        }

        return new Vector2(-1.0f, -1.0f);
    }


    private int GetMaxIndexOfVector3(Vector3 vec)
    {
        float max = -Mathf.Infinity;
        int index = -1;

        for (int i = 0; i < 3; i++)
        {
            if (vec[i] > max)
            {
                index = i;
                max = vec[i];
            }
        }

        return index;
    }


    private Vector3 GetWorldCoordsOfUVs(Vector2 uvs, Mesh mesh)
    {
        if (uvs.Equals(-Vector2.one))
        {
            return new Vector3(-1.0f, -1.0f, -1.0f);
        }


        int[] triangles = mesh.triangles;
        Vector2[] meshUVs = mesh.uv;
        Vector3[] vertices = mesh.vertices;

        for(int i = 0; i < triangles.Length; i += 3)
        {
            //get uvs
            Vector2 uv1 = meshUVs[triangles[i]];
            Vector2 uv2 = meshUVs[triangles[i+1]];
            Vector2 uv3 = meshUVs[triangles[i+2]];

            //calculate area of triangle
            float area = GetArea(uv1, uv2, uv3);
            if(area <= 0.0f)
            {
                continue;
            }

            //calculate barycentric coordinates, if negative skip it
            float a1 = GetArea(uv2, uv3, uvs) / area;
            if(a1 <= 0.0f)
            {
                continue;
            }

            float a2 = GetArea(uv3, uv1, uvs) / area;
            if (a2 <= 0.0f)
            {
                continue;
            }

            float a3 = GetArea(uv1, uv2, uvs) / area;
            if (a3 <= 0.0f)
            {
                continue;
            }

            // calculate position in local space
            Vector3 pos = a1 * vertices[triangles[i]] + a2 * vertices[triangles[i + 1]] + a3 * vertices[triangles[i + 2]];

            return transform.TransformPoint(pos);
        }

        return new Vector3(-1.0f, -1.0f, -1.0f);
    }

    private float GetArea(Vector2 uv1, Vector2 uv2, Vector2 uv3)
    {
        Vector2 side1 = uv1 - uv3;
        Vector2 side2 = uv2 - uv3;
        return (side1.x * side2.y - side1.y * side2.x) / 2.0f;
    }


    private void UpdateTilesWithAnimals(List<int> trackedTiles)
    {
        foreach(int tile in trackedTiles)
        {
            if (tilesWithAnimalsOfColor.ContainsKey(tile))
            {
                continue;
            }
            else
            {
                tilesWithAnimalsOfColor.Remove(tile);
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


    IEnumerator SpawnAnimal(Animal animal, Vector3 position, float spawnInterval, int number)
    {
        int numberSpawned = 0;

        while(numberSpawned < number)
        {
            numberSpawned++;
            Debug.Log("Has added animal");
            Instantiate(animal.gameObject, position + instantiationOffset, animal.transform.rotation, parent);
            yield return new WaitForSeconds(spawnInterval);
        }
    }
}
