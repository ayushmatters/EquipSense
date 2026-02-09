import React from 'react';
import '../../styles/auth.css';

const StepProgressBar = ({ currentStep, totalSteps, steps }) => {
    return (
        <div className="step-progress-container">
            <div className="step-progress-bar">
                {steps.map((step, index) => (
                    <React.Fragment key={index}>
                        <div className={`step-item ${currentStep >= index + 1 ? 'active' : ''} ${currentStep > index + 1 ? 'completed' : ''}`}>
                            <div className="step-circle">
                                {currentStep > index + 1 ? (
                                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                        <path d="M16.6666 5L7.49998 14.1667L3.33331 10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                    </svg>
                                ) : (
                                    <span className="step-number">{index + 1}</span>
                                )}
                            </div>
                            <div className="step-label">{step}</div>
                        </div>
                        {index < totalSteps - 1 && (
                            <div className={`step-line ${currentStep > index + 1 ? 'completed' : ''}`}></div>
                        )}
                    </React.Fragment>
                ))}
            </div>
        </div>
    );
};

export default StepProgressBar;
