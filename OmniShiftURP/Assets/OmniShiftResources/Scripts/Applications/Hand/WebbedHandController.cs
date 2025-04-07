using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;


[System.Serializable]
public class HandEvent : UnityEvent<Hand> { }

public class WebbedHandController : HandBehavior
{
    [Header("Applications")]

    public WebbedHandSets[] applicationSets;

    public WebbedHandSets activeSet;

    [Range(0.0f, 0.1f)]
    public float thumbThreshold;
    [Range(0.0f, 0.1f)]
    public float indexThreshold;
    [Range(0.0f, 0.1f)]
    public float middleThreshold;
    [Range(0.0f, 0.1f)]
    public float ringThreshold;

    [Header("Event handling")]
    public HandEvent handEvent;
    


    private void OnValidate()
    {
        if(applicationSets.Length > 0)
        {
            activeSet = applicationSets[0];
        }
        
    }

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        if (active)
        {
            Hand closestHand = GetNextHand();
            if (closestHand)
            {
                handEvent.Invoke(closestHand);
            }
            else
            {
                SetAllSetsTo(false);
                //SetImagesTo(false);
            }
        }
        else
        {
            SetAllSetsTo(false);
        }

    }

    
    

    public void ExecuteApplications(Hand hand)
    {
        switch (hand.gesture)
        {
            // maybe change this later for number or other gesture and select fixed set according to gesture
            case Hand.Gesture.Closed:

                if (hand.gestureChanged)
                {
                    // switch to next set
                    int activeIndex = (System.Array.IndexOf(applicationSets, activeSet) + 1) % applicationSets.Length;
                    ChangeApplicationSetTo(activeIndex);
                }
                

                break;
            case Hand.Gesture.Pointer:

                if (hand.gestureChanged)
                {
                    // switch to next set
                    int activeIndex = (System.Array.IndexOf(applicationSets, activeSet) + 1) % applicationSets.Length;
                    ChangeApplicationSetTo(activeIndex);
                }

                break;
            case Hand.Gesture.Open:
                // get the active applicaitons based on the fingere distanc to each other
                List<int> apps = GetActiveApplications(hand);
                activeSet.ExecuteApplications(apps, hand);
                
                break;
            default:
                Debug.LogError("Something went wrong in switch case statement");
                break;

        }

        activeSet.UpdateApplicationImage(hand);

        hand.gestureChanged = false;
    }


    private List<int> GetActiveApplications(Hand hand)
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

        List<int> activeApps = new List<int>();

        if(FingerClosed(hand, 2, 4, 5, 8, thumbThreshold))
        {
            activeApps.Add(0);
        }

        if (FingerClosed(hand, 5, 8, 9, 12, indexThreshold))
        {
            activeApps.Add(1);
        }

        if (FingerClosed(hand, 9, 12, 13, 16, middleThreshold))
        {
            activeApps.Add(2);
        }

        if (FingerClosed(hand, 13, 16, 17, 20, ringThreshold))
        {
            activeApps.Add(3);
        }
        

        return activeApps;
    }


    private void ChangeApplicationSetTo(int index)
    {
        activeSet = applicationSets[index];

        for (int i = 0; i < applicationSets.Length; i++)
        {
            applicationSets[i].SetActive(false);
        }

        activeSet.SetActive(true);
    }

    /// <summary>
    /// This determines if the fingers are closed by comparing how parallel they are via the crossproduct
    /// between the first and last joint of both fingers
    /// </summary>
    /// <param name="hand"></param>
    /// <param name="f1j1">Finger 1, joint 1</param>
    /// <param name="f1j2">Finger 1, joint 2</param>
    /// <param name="f2j1">Finger 2, joint 1</param>
    /// <param name="f2j2">Finger 2, joint 2</param>
    /// <param name="threshold"></param>
    /// <returns></returns>
    private bool FingerClosed(Hand hand, int f1j1, int f1j2, int f2j1, int f2j2, float threshold)
    {
        Vector3 finger1 = hand.jointsRep[f1j1].transform.position - hand.jointsRep[f1j2].transform.position;
        Vector3 finger2 = hand.jointsRep[f2j1].transform.position - hand.jointsRep[f2j2].transform.position;

        float parallelism = Vector3.Magnitude(Vector3.Cross(finger1.normalized, finger2.normalized));

        if (parallelism < threshold)
        {
            return true;
        }

        return false;
    }

    private float GetDistanceBetweenFingers(Hand hand, int joint1, int joint2)
    {
        return Vector3.Distance(hand.jointsRep[joint1].transform.position, hand.jointsRep[joint2].transform.position);
    }

    private void SetAllSetsTo(bool active)
    {
        for(int i = 0; i < applicationSets.Length; i++)
        {
            applicationSets[i].SetActive(active);
        }
    }

}
