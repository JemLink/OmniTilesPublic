using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class WebbedHandSets : MonoBehaviour
{
    // every set should have at most 4 applications

    public WebbedHandApplicationController[] set;
    public float scale = 1.0f;


    private void OnValidate()
    {
        if (set != null && set.Length > 4)
        {
            Debug.LogError("Cannot have more than 4 applications per hand");
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void SetActive(bool active)
    {
        for(int i = 0; i < set.Length; i++)
        {
            set[i].active = active;
        }

        SetImagesTo(active);
    }

    public void UpdateApplicationImage(Hand hand)
    {
        /// Mediapipes indexing is as follows:
        /// 0: wrist                     13: ring_MCP
        /// 1: thumb_CMC                 14: ring_PIP
        /// 2: thumb_MCP                 15: ring_DIP
        /// 3: thumb_IP                  16: ring_TIP
        /// 4: thumb_TIP                 17: pinky_MCP
        /// 5: index_MCP                 18: pinky_PIP
        /// 6: index_PIP                 19: pinky_DIP
        /// 7: index_DIP                 20: pinky_TIP
        /// 8: index_TIP
        /// 9: middle_MCP
        /// 10: middle_PIP
        /// 11: middle_DIP
        /// 12: middle_TIP
        /// 
        if (hand.gesture == Hand.Gesture.Open)
        {
            // thumb - index
            DisplayImageBetweenFinger(hand, 3, 7, set[0].gameObject);

            // index - middle
            DisplayImageBetweenFinger(hand, 7, 11, set[1].gameObject);

            // middle - ring
            DisplayImageBetweenFinger(hand, 11, 15, set[2].gameObject);

            // ring - little
            DisplayImageBetweenFinger(hand, 15, 19, set[3].gameObject);

        }
        else
        {
            SetImagesTo(false);
        }
    }

    private void DisplayImageBetweenFinger(Hand hand, int jointIndex1, int jointIndex2, GameObject image)
    {
        image.GetComponent<Renderer>().enabled = true;
        Vector3 jointVec = hand.jointsRep[jointIndex2].transform.position - hand.jointsRep[jointIndex1].transform.position;
        Vector3 imagePos = hand.jointsRep[jointIndex1].transform.position + 0.5f * jointVec;
        image.transform.position = imagePos;
        
        Quaternion imageRot = Quaternion.LookRotation(jointVec, Vector3.forward);
        imageRot *= Quaternion.Euler(180.0f, 90.0f, 0.0f);
        image.transform.rotation = imageRot;

        image.transform.localScale = new Vector3(jointVec.magnitude, jointVec.magnitude, jointVec.magnitude) * scale;
    }

    private void SetImagesTo(bool active)
    {
        for (int i = 0; i < set.Length; i++)
        {
            set[i].gameObject.GetComponent<Renderer>().enabled = active;
        }
    }


    public void ExecuteApplications(List<int> appsToActivate, Hand hand)
    {
        for(int i = 0; i < set.Length; i++)
        {
            if (appsToActivate.Contains(i))
            {
                set[i].ExecuteApplication(hand);
            }
            else
            {
                set[i].StopApplication();
            }
            
        }
    }
}
