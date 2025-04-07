using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;


/// <summary>
/// For now: This class should get a list of vertices and create an object based on them.
/// Later: Should receive a list of lists containing all tiles vertices
/// </summary>
[RequireComponent(typeof(MeshFilter))]
public class MeshGenerator : MonoBehaviour
{
    Mesh mesh;

    public Vector3[] vertices;
    public int[] triangles;

    Vector2[] uvs;
    

    // Start is called before the first frame update
    void Start()
    {
        //mesh = new Mesh();
        //GetComponent<MeshFilter>().mesh = mesh;
        //GetComponent<MeshCollider>().sharedMesh = mesh;

        //CreateShape(testVertices);
        //UpdateMesh();
    }

    // Update is called once per frame
    void Update()
    {

        //if (vertices != null && vertices.Length == 4)
        //{

        //    Debug.DrawLine(vertices[0], vertices[2], Color.red);
        //    Debug.DrawLine(vertices[1], vertices[3], Color.red);
        //}
    }


    /// <summary>
    /// This function recives an array of the vertices which should go clockwise around the tile
    /// Ex. Square: 0,1,2,3 (actually not id but screen position)
    /// 1------2
    /// |      |
    /// |      |
    /// 0------3
    /// </summary>
    /// <param name="vertices"></param>
    public void CreateMesh(Vector3[] vertices, Vector3 scale)
    {
        mesh = new Mesh();
        GetComponent<MeshFilter>().mesh = mesh;
        //GetComponent<MeshCollider>().sharedMesh = mesh;

        if(CreateShape(vertices, scale))
        {
            UpdateMesh();
        }
        
    }

    


    private bool CreateShape(Vector3[] vertices, Vector3 scale)
    {
        bool updatedSuccesful = false;

        vertices = UpdateScale(scale, vertices);

        this.vertices = vertices;

        switch (vertices.Length)
        {
            case 3:

                uvs = new Vector2[]
                {
                    new Vector2(0.0f, 0.0f),
                    new Vector2(1.0f, 0.0f),
                    new Vector2(1.0f, 1.0f)
                };

                triangles = new int[]
                {
                    2,1,0
                };
                updatedSuccesful = true;
                break;
            case 4:

                uvs = new Vector2[]
                {
                    new Vector2(0.0f, 0.0f),
                    new Vector2(1.0f, 0.0f),
                    new Vector2(1.0f, 1.0f),
                    new Vector2(0.0f, 1.0f)
                };

                triangles = new int[]
                {
                    2,1,0,
                    3,2,0
                };
                updatedSuccesful = true;
                break;
            case 5:
                
                uvs = new Vector2[]
                {
                    new Vector2(0.0f, 0.0f),
                    new Vector2(-0.2f, 0.8f),
                    new Vector2(0.5f, 1.0f),
                    new Vector2(1.2f, 0.8f),
                    new Vector2(1.0f, 0.0f)
                };

                this.triangles = new int[]
                {
                    2,1,0,
                    4,3,2,
                    4,2,0

                };

                updatedSuccesful = true;
                break;
            default:
                Debug.LogError("The number of vertices was not valid");
                updatedSuccesful = false;
                break;

        }


        return updatedSuccesful;
    }


    void UpdateMesh()
    {
        mesh.Clear();
        
        mesh.vertices = vertices;
        mesh.triangles = triangles;
        
        UpdateChildren();
        mesh.uv = uvs;
    }
        
    Vector3[] UpdateScale(Vector3 scale, Vector3[] vertices)
    {
        Vector3 center = Vector3.zero;

        for(int i = 0; i < vertices.Length; i++)
        {
            center += vertices[i];
        }

        center = center / (float)vertices.Length;

        for(int i = 0; i < vertices.Length; i++)
        {
            Vector3 newVert = (vertices[i] - center);
            newVert = new Vector3(newVert.x * scale.x, newVert.y * scale.y, newVert.z * scale.z);
            vertices[i] = newVert;
        }


        return vertices;
    }

    void UpdateChildren()
    {
        Vector3 center = GetCenter(vertices);
        Vector3 localUp = (vertices[1] + vertices[0]) * 0.5f - center;
        

        //Debug.DrawLine(vertices[0], vertices[2], Color.red);
        //Debug.DrawLine(vertices[1], vertices[3], Color.red);



        TileBehavior child = GetComponentInChildren<TileBehavior>();
        if (child)
        {
            child.transform.localScale = new Vector3(localUp.magnitude, localUp.magnitude, localUp.magnitude) * 2.0f;
            child.transform.rotation = Quaternion.LookRotation(Vector3.forward, localUp);
        }
        
        
    }

    


    private Vector3 GetCenter(Vector3[] vert)
    {
        Vector3 center = Vector3.zero;

        for(int i = 0; i < vert.Length; i++)
        {
            center = center + vert[i];
        }

        center = center / vert.Length;

        return center;
    }


    public Mesh GetMesh()
    {
        return mesh;
    }

    //private void OnDrawGizmos()
    //{
    //    if (vertices != null && vertices.Length == 4)
    //    {

    //        Gizmos.DrawSphere(transform.localPosition + vertices[0], 1.0f);
    //        Gizmos.DrawSphere(transform.localPosition + vertices[1], 1.0f);
    //        Gizmos.DrawSphere(transform.localPosition + vertices[2], 1.0f);
    //        Gizmos.DrawSphere(transform.localPosition + vertices[3], 1.0f);
    //    }
    //}

}
