using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CreateSpaceGround : TileBehavior
{
    public Texture2D spaceTex;

    public bool test;
    [Range(0.01f, 1.0f)]
    public float offset = 0.5f;

    // Start is called before the first frame update
    void Start()
    {
        
    }
    

    // Update is called once per frame
    void Update()
    {
        
    }

    public void CreateSpaceTile(List<TileShape> tiles)
    {
        foreach (TileShape tile in tiles)
        {
            // add collider for spaceship
            AddGravityField(tile);

            // update appearance
            // UpdateUVs(tile);

            Texture2D tex = tile.GetComponent<Renderer>().material.GetTexture("_BaseMap") as Texture2D;
            if (!tex)
            {
                Debug.Log("Updated space tex");
                tile.GetComponent<Renderer>().material.SetTexture("_BaseMap", spaceTex);
            }
            

        }
    }



    private void AddGravityField(TileShape tile)
    {
        MeshGenerator meshGen = tile.GetComponentInChildren<MeshGenerator>();
        Mesh mesh = meshGen.GetMesh();

        MeshCollider[] cols = meshGen.gameObject.GetComponents<MeshCollider>();
        cols = UpdateCollider(cols, meshGen, mesh);
        
        // creating the gravity script
        GravityOrbit orb = meshGen.GetComponent<GravityOrbit>();
        if (!orb)
        {
            orb = meshGen.gameObject.AddComponent<GravityOrbit>();
            orb.gravity = 20.0f;
            orb.fixedDirection = true;
            orb.gravityDirection = Vector3.forward;
            orb.toCamDirection = Vector3.up;
        }

        
    }


    private MeshCollider[] UpdateCollider(MeshCollider[] cols, MeshGenerator meshGen, Mesh mesh)
    {
        if (cols.Length != 2)
        {
            for(int i = 0; i < cols.Length; i++)
            {
                Destroy(cols[i]);
            }

            cols = new MeshCollider[2];
            cols[0] = meshGen.gameObject.AddComponent<MeshCollider>();
            cols[1] = meshGen.gameObject.AddComponent<MeshCollider>();
        }

        // the first collider will be the stable ground on which the ship is moving
        cols[0].sharedMesh = mesh;
        cols[0].convex = false;

        cols[1].sharedMesh = CreateExtendedMeshFrom(mesh, 2.0f);
        cols[1].convex = true;
        cols[1].isTrigger = true;

        return cols;
    }


    private Mesh CreateExtendedMeshFrom(Mesh mesh, float extension)
    {
        Mesh newMesh = Instantiate(mesh);
        Vector3[] vertices = newMesh.vertices;

        // create new vertices that are extented along z axis
        Vector3[] newVert = new Vector3[vertices.Length * 2]; 
        for(int i = 0; i < vertices.Length; i++)
        {
            newVert[i] = vertices[i];
            newVert[vertices.Length + i] = new Vector3(vertices[i].x, vertices[i].y, vertices[i].z - extension);
        }

        

        // create new triangles for the new vertices
        int[] oldTri = mesh.triangles;
        int[] tri = new int[oldTri.Length * 2];
        for(int i = 0; i < mesh.triangles.Length; i++)
        {
            // dublicating the bottom should be enough since the collider will bake the boundaries in between
            tri[i] = oldTri[i];
            tri[oldTri.Length + i] = vertices.Length + oldTri[i];
        }

        //Vector2[] uvs = new Vector2[newVert.Length];

        //for(int i = 0; i < uvs.Length; i++)
        //{
        //    uvs[i] = mesh.uv[i % mesh.uv.Length];
        //}
        

        newMesh.Clear();
        newMesh.vertices = newVert;
        newMesh.triangles = tri;
        //newMesh.uv = uvs;

        return newMesh;
    }


    private void UpdateUVs(TileShape tile)
    {
        MeshGenerator meshGen = tile.GetComponentInChildren<MeshGenerator>();
        Mesh mesh = meshGen.GetMesh();

        Vector3[] vertices = mesh.vertices;
        int[] triangles = mesh.triangles;

        Vector2[] uvs = new Vector2[vertices.Length];
        for(int i = 0; i < uvs.Length; i++)
        {
            uvs[i] = new Vector2(vertices[i].x, vertices[i].y) * offset;
        }

        mesh.Clear();
        mesh.vertices = vertices;
        mesh.triangles = triangles;
        mesh.uv = uvs;
    }
}
