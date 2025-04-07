using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CreateCollider : TileBehavior
{
    [Range(0.5f, 2.0f)]
    public float scale = 1.0f;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void CreateZoomTile(List<TileShape> tiles)
    {
        foreach (TileShape tile in tiles)
        {
            MeshGenerator meshGen = tile.GetComponentInChildren<MeshGenerator>();
            Mesh mesh = meshGen.GetMesh();

            MeshCollider[] cols = meshGen.gameObject.GetComponents<MeshCollider>();
            cols = UpdateCollider(cols, meshGen, mesh);

            tile.transform.localScale = new Vector3(scale, scale, scale);
        }
    }



    private MeshCollider[] UpdateCollider(MeshCollider[] cols, MeshGenerator meshGen, Mesh mesh)
    {
        if (cols.Length != 1)
        {
            for (int i = 0; i < cols.Length; i++)
            {
                Destroy(cols[i]);
            }

            cols = new MeshCollider[1];
            cols[0] = meshGen.gameObject.AddComponent<MeshCollider>();
        }

        // the first collider will be the stable ground on which the ship is moving
        cols[0].sharedMesh = CreateExtendedMeshFrom(mesh, 2.0f);
        cols[0].convex = true;
        cols[0].isTrigger = true;

        return cols;
    }

    private Mesh CreateExtendedMeshFrom(Mesh mesh, float extension)
    {
        Mesh newMesh = Instantiate(mesh);
        Vector3[] vertices = newMesh.vertices;

        // create new vertices that are extented along z axis
        Vector3[] newVert = new Vector3[vertices.Length * 2];
        for (int i = 0; i < vertices.Length; i++)
        {
            newVert[i] = vertices[i];
            newVert[vertices.Length + i] = new Vector3(vertices[i].x, vertices[i].y, vertices[i].z - extension);
        }



        // create new triangles for the new vertices
        int[] oldTri = mesh.triangles;
        int[] tri = new int[oldTri.Length * 2];
        for (int i = 0; i < mesh.triangles.Length; i++)
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
}
