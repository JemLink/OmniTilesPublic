using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TilesDataHandler : MonoBehaviour
{
    private TilesData data;
    public string message;

    [Header("Tile Handling")]
    string trianglesMessage;
    string squaresMessage;
    string pentagonMessage;

    [Header("Image handling")]
    private Texture2D tex;
    public Renderer rend;

    [Header("Tiles Handling and Conversion to Unity space")]
    public TilesHandler tilesHandler;
    public Vector2 imageSize = new Vector2(800.0f, 800.0f);
    [Range(5f, 50.0f)]
    public float XYMovement = 30.0f;
    [Range(-6.0f, 6.0f)]
    public float xOffset = 0.0f;
    [Range(-6.0f, 6.0f)]
    public float yOffset = 0.0f;
    [Range(0.5f, 20.0f)]
    public float distanceScale = 15.0f;
    //[Range(0.5f, 2.0f)]
    //public float scale = 1.0f;

    public List<string> squareList;

    // Start is called before the first frame update
    void Start()
    {
        if (rend)
        {
            tex = new Texture2D(2, 2, TextureFormat.RGB24, mipChain: false);
            rend.material.SetTexture("_BaseMap", tex);
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public void SetMessage(string message)
    {
        this.message = message;
    }

    public string GetMessage()
    {
        return message;
    }

    public void SetData(TilesData data)
    {
        this.data = data;

        UpdateImage(data);
        UpdateText(data);
    }

    public TilesData GetData()
    {
        return data;
    }


    public void UpdateImage(TilesData d)
    {
        if (rend)
        {
            tex.LoadImage(d.image);
        }
    }

    public void UpdateText(TilesData d)
    {
        trianglesMessage = d.trianglesMessage;
        squaresMessage = d.squaresMessage;
        pentagonMessage = d.pentagonsMessage;

        message = trianglesMessage + squaresMessage + pentagonMessage;

        //Debug.Log("Message " + message);

        UpdateHandler();
    }

    private void UpdateHandler()
    {
        squareList = new List<string>();
        // create Triangle list
        List<Triangle> triangles = GetListOfTiles<Triangle>(trianglesMessage); //ConvertTilesTo<Triangle>(GetListOfTiles(trianglesMessage));
        // create squares list
        List<Square> squares = GetListOfTiles<Square>(squaresMessage);
        // create pentagon list
        List<Pentagon> pentagons = GetListOfTiles<Pentagon>(pentagonMessage);

        // update triangles
        tilesHandler.UpdateTriangles(triangles);
        // update squares
        tilesHandler.UpdateSquares(squares);
        // update pentagons
        tilesHandler.UpdatePentagons(pentagons);

    }

    /// <summary>
    /// This takes a message of the form:
    /// [id, (x, y, z), (xRot, yRot, zRot)][...][...]
    /// New Message: vertices are divided by v and then given in their x and z value (y will always be 0)
    /// [id, (x, y, z), (v vx,vz v v2x,v2z v...)][...][...]
    /// 
    /// </summary>
    /// <param name="message"></param>
    /// <returns></returns>
    private List<T> GetListOfTiles<T>(string message) where T : TileShape, new()
    {
        List<T> tiles = new List<T>();
        
        string[] singleTiles = message.Split('[');

        for (int i = 1; i < singleTiles.Length; i++)
        {
            string[] transforms = singleTiles[i].Split('(');

            // first entry before the bracket is the id, 
            int id = int.Parse(transforms[0].Substring(0, transforms[0].Length - 1));

            // to get rid of the bracket in x, y, z),
            string positionString = transforms[1].Substring(0, transforms[1].Length - 2);
            // to get rid of the brackets in x, y, z)]
            string verticesString = transforms[2].Substring(0, transforms[2].Length - 2);

            string[] pos = positionString.Split(',');
            float x = float.Parse(pos[0]);
            float y = float.Parse(pos[1]);
            float z = 0.0f; // float.Parse(pos[2]);

            // need to convert to unity space
            Vector3 unityPos = ConvertFromOpenCVToUnitySpace(new Vector3(x, y, z));
            
            string[] singleVertices = verticesString.Split('v');
            // -1 since the first string is the empty string before the first v
            Vector3[] vertices = new Vector3[singleVertices.Length - 1];
            for(int j = 0; j < vertices.Length; j++)
            {
                string[] vert = singleVertices[j + 1].Split(',');
                float vx = float.Parse(vert[0]);
                float vy = float.Parse(vert[1]); 
                float vz = 0.0f;

                //print("VerticePython: " + new Vector3(vx, vy, vz));

                vertices[j] = ConvertFromOpenCVToUnitySpace(new Vector3(vx, vy, vz));
            }

            T tmpTile = new T
            {
                id = id,
                position = unityPos,
                vertices = vertices
            };

            //tmpTile.transform.localScale = new Vector3(tmpTile.transform.localScale.x * scale, tmpTile.transform.localScale.y * scale, tmpTile.transform.localScale.z * scale);
            tiles.Add(tmpTile);
            squareList.Add(id + ", " + unityPos.ToString() + ", " + vertices);
        }

        tiles = DeleteDoubledTiles(tiles);

        return tiles;
    }


    private List<T> DeleteDoubledTiles<T>(List<T> tiles) where T : TileShape, new()
    {
        List<int> IDs = new List<int>();
        List<T> returnList = new List<T>();
        for(int i = 0; i < tiles.Count; i++)
        {
            if (!IDs.Contains(tiles[i].id))
            {
                returnList.Add(tiles[i]);
                IDs.Add(tiles[i].id);
            }
        }

        return returnList;
    }


    private List<T> ConvertTilesTo<T>(List<TileShape> tiles) where T : TileShape, new()
    {
        List<T> returnList = new List<T>();
        for(int i = 0; i < tiles.Count; i++)
        {
            returnList.Add((T)tiles[i]);
        }

        return returnList;
    }


    private Vector3 ConvertFromOpenCVToUnitySpace(Vector3 openCVCoords)
    {
        //Debug.Log("open cv: " + openCVCoords);
        // map to range of 0 to 1
        float x = (openCVCoords.x / imageSize.x);
        float y = (openCVCoords.y / imageSize.y);
        
        // map of range from 0,1 to -1,1
        x = (x * 2.0f) - 1;//-(x * 2.0f) + 1; // x must be flipped since opencv has different handed coordinate system
        y = (y * 2.0f) - 1;

        x *= XYMovement;
        y *= XYMovement;

        x += xOffset;
        y += yOffset;

        // z is in cm while Unity is in m
        // need to change it and adapt to camera pos
        float z = openCVCoords.z * 0.01f * distanceScale; // this is to change it to m

        return new Vector3(x, y, z);

    }


    private Vector3 GetPositionFromVertices(Vector3[] vertices)
    {
        Vector3 returnVec = (vertices[2] - vertices[0]) *0.5f;
        return returnVec;
    }

    public void SetXOffset(float xOffset)
    {
        this.xOffset = xOffset;
    }

    public void SetYOffset(float yOffset)
    {
        this.yOffset = yOffset;
    }

    public void SetZOffset(float zOffset)
    {
        distanceScale = zOffset;
    }

    public void SetXYMovement(float XYMovement)
    {
        this.XYMovement = XYMovement;
    }
}
