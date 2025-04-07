using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TileShape : MonoBehaviour
{
    public int id;
    public int prevID;
    public Vector3 position;
    public Quaternion rotation;

    public bool updated = false;

    private int textureID = 0;
    public bool destroyWhenNotDetected = true;
    public bool notDetected = false;


    public Vector3[] vertices;



    public TileShape() { }

    public TileShape(int id)
    {
        this.id = id;
        prevID = id;
    }

    public TileShape(int id, Vector3 position, Vector3[] vertices)
    {
        this.id = id;
        prevID = id;
        //this.position = position;
        //this.rotation = Quaternion.Euler(rotation);
        this.vertices = vertices;
        UpdatePosition();
    }

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    /// <summary>
    /// This function updates the position to the center of vertices
    /// </summary>
    public void UpdatePosition()
    {
        Vector3 pos = Vector3.zero;
        for (int i = 0; i < vertices.Length; i++)
        {
            pos = pos + vertices[i];
        }

        this.position = pos / (float)vertices.Length;
    }

    public void SetPosition(Vector3 newPos)
    {
        this.position = newPos;
        transform.localPosition = newPos;
    }

    //public void UpdateRotation(Quaternion rotation)
    //{
    //    this.rotation = rotation;
    //    transform.rotation = rotation;
    //}

    public void UpdateVertices(Vector3[] vertices)
    {
        this.vertices = vertices;
    }

    public void UpdateTile(int id, Vector3 pos, Quaternion rot)
    {
        this.id = id;
        SetPosition(pos);
        //UpdateRotation(rot);
        UpdateVertices(vertices);
        updated = true;
        //Debug.Log("Updated " + this.id);
    }

    public void UpdateTile(int id, Vector3 pos, Vector3[] vertices)//Quaternion rot)
    {
        this.id = id;
        SetPosition(pos);
        //UpdateRotation(rot);
        UpdateVertices(vertices);
        updated = true;
        //Debug.Log("Updated " + this.id);
    }

    
    public int GetTextureID()
    {
        return textureID;
    }

    public void SetTextureID(int id)
    {
        textureID = id;
    }

}
